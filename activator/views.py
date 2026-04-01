from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import requests
import json
from new_check import submit_order
from .models import Order, Key
import logging

logger = logging.getLogger(__name__)

# Переводы для сообщений об ошибках
TRANSLATIONS = {
    'EN': {
        'key_required': 'Key is required',
        'key_short': 'Key is too short',
        'key_available': 'Key verified successfully!',
        'key_used': 'This key has already been used',
        'key_expired': 'This key has expired',
        'key_invalid': 'Please enter a valid key',
        'key_error': 'Invalid key or unknown status',
        'key_check_error': 'Error checking key',
        'auth_required': 'AuthSession is required',
        'json_invalid': 'Invalid JSON format',
        'session_verified': 'Session verified! Email: {email}',
        'session_expired': 'Session has expired. Please login again.',
        'token_expired': 'Access token has expired. Please get a fresh session.',
        'account_problem': 'Your account has issues (delinquent). Please resolve them first.',
        'user_mismatch': 'User ID mismatch between session and token.',
        'email_mismatch': 'Email mismatch between session and token.',
        'plan_mismatch': 'Plan type mismatch between session and token.',
        'plan_not_free': 'You already have an active subscription, try again later.',
        'missing_data': 'Missing required data (user or accessToken). Please paste the complete AuthSession data.',
        'invalid_user_data': 'Invalid user data. User must have id and email.',
        'invalid_access_token': 'Invalid access token format.',
        'invalid_expires': 'Invalid expires format in session.',
        'cannot_activate': 'Cannot activate: {error}',
        'activation_success': '🎉 Activation Complete! Your subscription has been activated successfully. Refresh the target page to see the changes.',
        'activation_error': 'Failed to activate the key.',
        'missing_code': 'Activation key is missing. Please enter your key and try again.',
        'missing_session': 'Session data is missing. Please paste your ChatGPT AuthSession JSON.',
        'invalid_session': 'Invalid session JSON. Please copy the full AuthSession data again.',
        'invalid_code': 'The activation key was not found. Please check the key and try again.',
        'code_used': 'This activation key has already been used.',
        'database_error': 'Server database error. Please try again in a few minutes.',
        'workflow_error': 'Order processing failed. Please try again shortly.',
        'plan_warning_go': 'You have a Go subscription. Continuing will update it to Plus.',
        'plan_warning_pro': 'You have a Pro subscription. Continuing will update it to Plus.',
        'plan_plus_blocked': 'Your Plus subscription will be updated.',
        'plan_check_unknown': 'Could not detect your current plan. Continuing may overwrite your current subscription. Press OK to continue.',
        'server_error': 'Server error. Please try again later.',
    },
    'RU': {
        'key_required': 'Требуется ввести ключ',
        'key_short': 'Ключ слишком короткий',
        'key_available': 'Ключ успешно проверен!',
        'key_used': 'Этот ключ уже использован',
        'key_expired': 'Ключ истек',
        'key_invalid': 'Пожалуйста, введите правильный ключ',
        'key_error': 'Неправильный ключ или неизвестный статус',
        'key_check_error': 'Ошибка при проверке ключа',
        'auth_required': 'AuthSession требуется',
        'json_invalid': 'Неверный формат JSON',
        'session_verified': 'Сессия проверена! Email: {email}',
        'session_expired': 'Сессия истекла. Пожалуйста, войдите снова.',
        'token_expired': 'Access токен истек. Получите новую сессию.',
        'account_problem': 'У вашего аккаунта есть проблемы (задолженность). Разрешите их сначала.',
        'user_mismatch': 'Несоответствие ID пользователя между сессией и токеном.',
        'email_mismatch': 'Несоответствие email между сессией и токеном.',
        'plan_mismatch': 'Несоответствие типа плана между сессией и токеном.',
        'plan_not_free': 'У вас уже есть действующая подписка, попробуйте позже.',
        'missing_data': 'Отсутствуют требуемые данные (user или accessToken). Вставьте полные данные AuthSession.',
        'invalid_user_data': 'Неверные данные пользователя. Пользователь должен иметь id и email.',
        'invalid_access_token': 'Неверный формат access токена.',
        'invalid_expires': 'Неверный формат expires в сессии.',
        'cannot_activate': 'Не удалось активировать: {error}',
        'activation_success': '🎉 Активация завершена! Ваша подписка успешно активирована. Обновите целевую страницу, чтобы увидеть изменения.',
        'activation_error': 'Не удалось активировать ключ.',
        'missing_code': 'Ключ активации не передан. Введите ключ и попробуйте снова.',
        'missing_session': 'Данные сессии не переданы. Вставьте JSON AuthSession ChatGPT.',
        'invalid_session': 'Неверный JSON сессии. Скопируйте полный AuthSession и попробуйте снова.',
        'invalid_code': 'Указанный ключ не найден. Проверьте ключ и попробуйте снова.',
        'code_used': 'Этот ключ уже был использован.',
        'database_error': 'Ошибка базы данных на сервере. Попробуйте через несколько минут.',
        'workflow_error': 'Ошибка запуска обработки заказа. Попробуйте чуть позже.',
        'plan_warning_go': 'У вас подписка Go. При продолжении она обновится на Plus.',
        'plan_warning_pro': 'У вас подписка Pro. При продолжении она обновится на Plus.',
        'plan_plus_blocked': 'Ваша подписка Plus обновится.',
        'plan_check_unknown': 'Не удалось определить текущий план. При продолжении текущая подписка может быть перезаписана. Нажмите OK, чтобы продолжить.',
        'server_error': 'Ошибка сервера. Попробуйте позже.',
    },
    'CN': {
        'key_required': '需要输入密钥',
        'key_short': '密钥太短',
        'key_available': '密钥验证成功！',
        'key_used': '此密钥已被使用',
        'key_expired': '密钥已过期',
        'key_invalid': '请输入有效的密钥',
        'key_error': '无效的密钥或未知状态',
        'key_check_error': '检查密钥时出错',
        'auth_required': '需要 AuthSession',
        'json_invalid': '无效的 JSON 格式',
        'session_verified': '会话已验证！Email: {email}',
        'session_expired': '会话已过期。请重新登录。',
        'token_expired': '访问令牌已过期。请获取新会话。',
        'account_problem': '您的账户存在问题（欠款）。请先解决。',
        'user_mismatch': '会话和令牌之间的用户 ID 不匹配。',
        'email_mismatch': '会话和令牌之间的电子邮件不匹配。',
        'plan_mismatch': '会话和令牌之间的计划类型不匹配。',
        'plan_not_free': '您已经有有效的订阅，请稍后重试.',
        'missing_data': '缺少必需的数据（user 或 accessToken）。请粘贴完整的 AuthSession 数据。',
        'invalid_user_data': '用户数据无效。用户必须有 id 和 email。',
        'invalid_access_token': '访问令牌格式无效。',
        'invalid_expires': '会话中的 expires 格式无效。',
        'cannot_activate': '无法激活：{error}',
        'activation_success': '🎉 激活完成！您的订阅已成功激活。刷新目标页面以查看更改。',
        'activation_error': '无法激活密钥。',
        'missing_code': '缺少激活密钥。请输入密钥后重试。',
        'missing_session': '缺少会话数据。请粘贴 ChatGPT AuthSession JSON。',
        'invalid_session': '会话 JSON 无效。请重新复制完整 AuthSession 数据。',
        'invalid_code': '未找到该激活密钥。请检查后重试。',
        'code_used': '该激活密钥已被使用。',
        'database_error': '服务器数据库错误，请稍后再试。',
        'workflow_error': '订单处理流程错误，请稍后重试。',
        'plan_warning_go': '您有 Go 订阅。继续将更新为 Plus。',
        'plan_warning_pro': '您有 Pro 订阅。继续将更新为 Plus。',
        'plan_plus_blocked': '您的 Plus 订阅将更新。',
        'plan_check_unknown': '无法识别当前订阅。继续可能会覆盖当前订阅。点击 OK 继续。',
        'server_error': '服务器错误。请稍后重试。',
    }
}

SUBMIT_ORDER_ERROR_MESSAGES = {
    'MISSING_CODE': 'missing_code',
    'MISSING_SESSION': 'missing_session',
    'INVALID_SESSION': 'invalid_session',
    'INVALID_CODE': 'invalid_code',
    'CODE_USED': 'code_used',
    'DATABASE_ERROR': 'database_error',
    'WORKFLOW_ERROR': 'workflow_error',
}

def get_message(key, lang='EN', **kwargs):
    """获取指定语言的翻译消息"""
    lang = lang.upper() if lang else 'EN'
    if lang not in TRANSLATIONS:
        lang = 'EN'
    
    message = TRANSLATIONS[lang].get(key, TRANSLATIONS['EN'].get(key, key))
    
    # 替换占位符
    if kwargs:
        try:
            message = message.format(**kwargs)
        except (KeyError, IndexError):
            pass
    
    return message


def index(request):
    return render(request, 'index.html')


@csrf_exempt
@require_http_methods(["POST"])
def check_key_status(request):
    """Упрощенная проверка ключа: минимальная длина + проверка использованности в БД."""

    try:
        data = json.loads(request.body)
        key = data.get('key', '').strip()
        lang = data.get('lang', 'EN')

        if not key:
            return JsonResponse({'status': 'error', 'message': get_message('key_required', lang)}, status=400)

        if len(key) < 5:
            return JsonResponse({'status': 'error', 'message': get_message('key_short', lang)}, status=400)

        key_obj = Key.objects.filter(key__iexact=key).first()
        if Order.objects.filter(key__iexact=key).exists() or (key_obj and key_obj.is_used):
            return JsonResponse({
                'status': 'used',
                'message': get_message('key_used', lang),
                'key': key
            }, status=200)

        return JsonResponse({
            'status': 'available',
            'message': get_message('key_available', lang),
            'key': key
        }, status=200)

    except json.JSONDecodeError as e:
        logger.error(f'JSON decode error in check_key_status: {str(e)}')
        return JsonResponse({'status': 'error', 'message': get_message('json_invalid', 'EN')}, status=400)
    except Exception as e:
        logger.error(f'Unexpected error in check_key_status: {str(e)}', exc_info=True)
        return JsonResponse({'status': 'error', 'message': get_message('server_error', 'EN')}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def verify_chatgpt_token(request):
    """Упрощённая проверка - просто проверяем что данные не пустые"""
    
    try:
        data = json.loads(request.body)
        auth_session = data.get('auth_session', '').strip()
        lang = data.get('lang', 'EN')
        
        if not auth_session:
            return JsonResponse({'status': 'error', 'message': get_message('auth_required', lang)}, status=400)
        
        # Без каких-либо проверок - просто возвращаем success
        return JsonResponse({
            'status': 'success',
            'message': get_message('session_verified', lang, email='N/A'),
            'user_email': 'N/A',
            'plan': 'N/A',
            'expires': 'N/A'
        }, status=200)
        
    except json.JSONDecodeError as e:
        logger.error(f'JSON decode error in verify_chatgpt_token: {str(e)}')
        return JsonResponse({'status': 'error', 'message': get_message('json_invalid', 'EN')}, status=400)
    except Exception as e:
        logger.error(f'Unexpected error in verify_chatgpt_token: {str(e)}', exc_info=True)
        try:
            lang = data.get('lang', 'EN')
        except:
            lang = 'EN'
        return JsonResponse({'status': 'error', 'message': get_message('server_error', lang)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def activate_key(request):
    """Активация ключа с AuthSession токеном"""
    
    try:
        data = json.loads(request.body)
        key = data.get('key', '').strip().upper()
        auth_session = data.get('auth_session', '').strip()
        lang = data.get('lang', 'EN')
        
        logger.info(f"=== ACTIVATE KEY REQUEST ===")
        logger.info(f"Key: {key}")
        logger.info(f"Auth session length: {len(auth_session)}")
        logger.info(f"Lang: {lang}")
        
        if not key:
            logger.warning("Key is missing")
            return JsonResponse({'status': 'error', 'message': get_message('key_required', lang)}, status=400)
        
        if not auth_session:
            logger.warning("Auth session is missing")
            return JsonResponse({'status': 'error', 'message': get_message('auth_required', lang)}, status=400)

        if Order.objects.filter(key__iexact=key).exists():
            logger.warning(f"Key already used in local orders DB: {key}")
            return JsonResponse({'status': 'error', 'message': get_message('code_used', lang)}, status=400)
        
        # Активируем ключ (передаём auth_session как есть, без парсинга)
        try:
            logger.info(f"Calling submit_order with raw auth_session...")
            result = submit_order(auth_session, key)
            logger.info(f"submit_order result: {result}")

            if result == 'success':
                # Сохраняем в БД при успешной активации
                try:
                    # Создаем запись в БД
                    order = Order.objects.create(
                        key=key,
                        token=auth_session
                    )

                    Key.objects.filter(key__iexact=key).update(is_used=True)
                    
                    logger.info(f"Order saved: {order.id} - Key: {key} - Time: {order.created_at}")
                except Exception as e:
                    logger.error(f"Error saving order: {str(e)}")
                    # Не прерываем процесс, если не удалось сохранить в БД
                
                return JsonResponse({
                    'status': 'success',
                    'message': get_message('activation_success', lang)
                }, status=200)
            else:
                msg_key = SUBMIT_ORDER_ERROR_MESSAGES.get(result, 'activation_error')
                error_msg = get_message(msg_key, lang)
                logger.warning(f"submit_order returned: {result}")
                logger.info(f"Mapped to message key: {msg_key}")
                return JsonResponse({
                    'status': 'error',
                    'message': error_msg
                }, status=400)
                
        except Exception as e:
            logger.error(f'Key activation API error: {str(e)}', exc_info=True)
            return JsonResponse({
                'status': 'error',
                'message': get_message('server_error', lang)
            }, status=500)
        
    except json.JSONDecodeError as e:
        logger.error(f'JSON decode error in activate_key: {str(e)}')
        return JsonResponse({'status': 'error', 'message': get_message('json_invalid', 'EN')}, status=400)
    except Exception as e:
        logger.error(f'Unexpected error in activate_key: {str(e)}', exc_info=True)
        try:
            lang = data.get('lang', 'EN')
        except:
            lang = 'EN'
        return JsonResponse({'status': 'error', 'message': get_message('server_error', lang)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def check_subscription_plan(request):
    """Проверка типа плана перед активацией."""

    try:
        data = json.loads(request.body)
        auth_session = data.get('auth_session', '').strip()
        lang = data.get('lang', 'EN')

        if not auth_session:
            return JsonResponse({'status': 'error', 'message': get_message('auth_required', lang)}, status=400)

        try:
            auth_data = json.loads(auth_session)
        except json.JSONDecodeError:
            # Do not block user: ask confirmation if plan can't be parsed.
            return JsonResponse({
                'status': 'warning',
                'plan': 'unknown',
                'requires_confirmation': True,
                'message': get_message('plan_check_unknown', lang)
            }, status=200)

        raw_plan = str(auth_data.get('account', {}).get('planType', '')).strip().lower()
        logger.info(f"Plan detected from AuthSession: {raw_plan}")

        if raw_plan == 'free':
            return JsonResponse({
                'status': 'ok',
                'plan': 'free',
                'requires_confirmation': False
            }, status=200)

        if raw_plan in ['go', 'pro']:
            msg_key = f'plan_warning_{raw_plan}'
            return JsonResponse({
                'status': 'warning',
                'plan': raw_plan,
                'requires_confirmation': True,
                'message': get_message(msg_key, lang)
            }, status=200)

        if raw_plan in ['plus', 'chatgptplus', 'chatgpt_plus', 'gpt_plus']:
            return JsonResponse({
                'status': 'warning',
                'plan': 'plus',
                'requires_confirmation': True,
                'message': get_message('plan_plus_blocked', lang)
            }, status=200)

        # Unknown plan: allow only after explicit confirmation.
        return JsonResponse({
            'status': 'warning',
            'plan': raw_plan or 'unknown',
            'requires_confirmation': True,
            'message': get_message('plan_check_unknown', lang)
        }, status=200)

    except json.JSONDecodeError as e:
        logger.error(f'JSON decode error in check_subscription_plan: {str(e)}')
        return JsonResponse({'status': 'error', 'message': get_message('json_invalid', 'EN')}, status=400)
    except Exception as e:
        logger.error(f'Unexpected error in check_subscription_plan: {str(e)}', exc_info=True)
        try:
            lang = data.get('lang', 'EN')
        except:
            lang = 'EN'
        return JsonResponse({'status': 'error', 'message': get_message('server_error', lang)}, status=500)