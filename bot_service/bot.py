import os
import sys
import django

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'keyactivate.settings')
django.setup()

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from activator.models import Key, OrderKeyTg
from environs import Env
import logging
from django.db import transaction
import threading

from crypto_pay import create_invoice, check_invoice

# ---------------- LOGGING ----------------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# ---------------- ENV ----------------
env = Env()
env.read_env()

bot = telebot.TeleBot(env.str('TELEGRAM_TOKEN'))

user_data = {}

# ---------------- TAKE KEY ----------------
def take_key(tariff):
    with transaction.atomic():
        key = Key.objects.select_for_update().filter(
            tariff=tariff,
            is_used=False
        ).first()

        if not key:
            return None

        key.is_used = True
        key.save()

        return key


# ---------------- RELEASE KEY ----------------
def release_key(key_id, chat_id):
    try:
        key = Key.objects.get(id=key_id)

        if user_data.get(chat_id) and user_data[chat_id].get('key_id') == key_id:
            key.is_used = False
            key.save()

            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton('🔙 Назад', callback_data='buy'))

            bot.send_message(
                chat_id,
                '⏰ Время оплаты истекло.\nПопробуйте снова.',
                reply_markup=markup
            )

            user_data.pop(chat_id, None)

    except Exception as e:
        logger.error(f'Error releasing key: {e}')


# ---------------- MAIN MENU ----------------
def main_menu(chat_id, message_id=None):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('🛒 Купить ключ', callback_data='buy'))
    markup.add(InlineKeyboardButton('🆘 Поддержка', callback_data='support'))

    text = (
        '🔑 Здесь вы можете приобрести ключ для доступа к PLUS\n\n'
        '💎 Доступные тарифы:\n'
        '🟢 1 месяц — быстрый старт\n'
        '🔵 1 год — максимальная выгода\n\n'
        '⚡ После оплаты вы получите ключ мгновенно\n\n'
        '👇 Нажмите кнопку ниже, чтобы продолжить'
    )

    if message_id:
        bot.edit_message_text(
            text,
            chat_id,
            message_id,
            reply_markup=markup
        )
    else:
        bot.send_message(
            chat_id,
            text,
            reply_markup=markup
        )


# ---------------- START ----------------
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, '👋 Добро пожаловать в AlbikStore!')
    main_menu(message.chat.id)


# ---------------- BUY ----------------
@bot.callback_query_handler(func=lambda call: call.data == 'buy')
def buy(call):
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton('🟢 PLUS 1 мес. — $3', callback_data='month'),
        InlineKeyboardButton('🔵 PLUS 1 год — $32', callback_data='year')
    )
    markup.add(InlineKeyboardButton('🔙 Назад', callback_data='menu'))

    bot.edit_message_text(
        '💼 Выберите тариф:',
        call.message.chat.id,
        call.message.message_id,
        reply_markup=markup
    )


# ---------------- TARIFF ----------------
@bot.callback_query_handler(func=lambda call: call.data in ['month', 'year'])
def tariff(call):
    chat_id = call.message.chat.id
    tariff = call.data

    key = take_key(tariff)

    if not key:
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton('🔙 Назад', callback_data='buy'))

        bot.edit_message_text(
            '❌ Ключи закончились.\nПопробуйте позже.',
            chat_id,
            call.message.message_id,
            reply_markup=markup
        )
        return

    price = 0.1 if tariff == 'month' else 0.1

    try:
        payload = f'{chat_id}:{key.id}'
        invoice = create_invoice(payload, price)

        user_data[chat_id] = {
            'tariff': tariff,
            'key_id': key.id,
            'invoice_id': invoice['invoice_id']
        }

        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton('💳 Оплатить', url=invoice['pay_url']))
        markup.add(InlineKeyboardButton('✅ Я оплатил', callback_data='check_payment'))
        markup.add(InlineKeyboardButton('🔙 Назад', callback_data='buy'))

        bot.edit_message_text(
            '💸 Оплатите ⏰в ТЕЧЕНИЕ 10 МИНУТ⏰ по ссылке ниже\n'
            'и нажмите "Я оплатил":',
            chat_id,
            call.message.message_id,
            reply_markup=markup
        )

        threading.Timer(600, release_key, args=[key.id, chat_id]).start()

    except Exception as e:
        logger.error(e)
        bot.send_message(chat_id, '❌ Ошибка создания оплаты')


# ---------------- CHECK PAYMENT ----------------
@bot.callback_query_handler(func=lambda call: call.data == 'check_payment')
def check_payment(call):
    chat_id = call.message.chat.id
    data = user_data.get(chat_id)

    if not data:
        bot.send_message(chat_id, '⏰ Время истекло. Попробуйте снова.')
        return

    try:
        status = check_invoice(data['invoice_id'])

        if status == 'paid':
            key = Key.objects.get(id=data['key_id'])

            bot.edit_message_text(
                '✅ Оплата прошла успешно!',
                chat_id,
                call.message.message_id
            )

            OrderKeyTg.objects.create(key=key.key, tg_id=chat_id)
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton('🔗 Сайт для активаций', url='https://gptactivation.store/'))
            bot.send_message(
                chat_id,
                f'🎉 Оплата подтверждена!\n\n'
                f'🔑 Ваш ключ:\n{key.key}\n\n'
                '❗ Важно:\n\n'
                '— Не передавайте ключ другим\n'
                '— Один ключ = один аккаунт\n'
                '— При проблемах обратитесь в поддержку\n\n'
                '💬 Поддержка доступна в меню\n\n'
                '👇 Нажмите кнопку ниже для перехода на сайт для активации',
                reply_markup=markup
            )

            user_data.pop(chat_id, None)

        else:
            bot.send_message(
                chat_id,
                '❌ Оплата не найдена.\n'
                'Сначала оплатите и попробуйте снова.'
            )

    except Exception as e:
        logger.error(e)
        bot.send_message(chat_id, '⚠️ Ошибка проверки оплаты')


@bot.callback_query_handler(func=lambda call: call.data == 'support')
def support(call):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('💬 Написать оператору', url='https://t.me/morginfp'))
    markup.add(InlineKeyboardButton('🔙 Назад', callback_data='menu'))

    bot.edit_message_text(
        '🆘 Поддержка\n\n'
        'Если у вас возникли вопросы или проблемы с оплатой —\n'
        'напишите нашему оператору.\n\n'
        '⏱ Обычно отвечаем быстро.',
        call.message.chat.id,
        call.message.message_id,
        reply_markup=markup
    )

# ---------------- MENU ----------------
@bot.callback_query_handler(func=lambda call: call.data == 'menu')
def menu(call):
    main_menu(call.message.chat.id, call.message.message_id)


# ---------------- RUN ----------------
logger.info('Bot started')
bot.infinity_polling()