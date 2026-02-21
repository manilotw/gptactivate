from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import requests
import json
from parse_keys import check_key_status as check_key_via_api, activate_key as activate_key_via_api
from valid_token import check_chatgpt_session
from .models import Order
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
        'server_error': '服务器错误。请稍后重试。',
    }
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


@require_http_methods(["POST"])
def check_key_status(request):
    """Проверка статуса ключа через внешний API"""
    
    try:
        data = json.loads(request.body)
        key = data.get('key', '').strip().upper()
        lang = data.get('lang', 'EN')
        
        if not key:
            return JsonResponse({'status': 'error', 'message': get_message('key_required', lang)}, status=400)
        
        if len(key) < 8:
            return JsonResponse({'status': 'error', 'message': get_message('key_short', lang)}, status=400)
        
        # Проверяем ключ через внешний API
        try:
            key_status = check_key_via_api(key)
            
            if key_status == 'available':
                return JsonResponse({
                    'status': 'available',
                    'message': get_message('key_available', lang),
                    'key': key
                }, status=200)
            elif key_status == 'used':
                return JsonResponse({
                    'status': 'error',
                    'message': get_message('key_used', lang)
                }, status=400)
            elif key_status == 'expired':
                return JsonResponse({
                    'status': 'error',
                    'message': get_message('key_expired', lang)
                }, status=400)
            elif key_status == 'invalid':
                return JsonResponse({
                    'status': 'error',
                    'message': get_message('key_invalid', lang)
                }, status=400)
            else:
                return JsonResponse({
                    'status': 'error',
                    'message': get_message('key_error', lang)
                }, status=400)
                
        except Exception as e:
            logger.error(f'Key check API error: {str(e)}', exc_info=True)
            return JsonResponse({
                'status': 'error',
                'message': get_message('key_check_error', lang)
            }, status=500)
        
    except json.JSONDecodeError as e:
        logger.error(f'JSON decode error in check_key_status: {str(e)}')
        return JsonResponse({'status': 'error', 'message': get_message('json_invalid', 'EN')}, status=400)
    except Exception as e:
        logger.error(f'Unexpected error in check_key_status: {str(e)}', exc_info=True)
        return JsonResponse({'status': 'error', 'message': get_message('server_error', 'EN')}, status=500)


@require_http_methods(["POST"])
def verify_chatgpt_token(request):
    """Проверка ChatGPT AuthSession через детальную проверку"""
    
    try:
        data = json.loads(request.body)
        auth_session = data.get('auth_session', '').strip()
        lang = data.get('lang', 'EN')
        
        if not auth_session:
            return JsonResponse({'status': 'error', 'message': get_message('auth_required', lang)}, status=400)
        
        # Парсим JSON
        try:
            auth_data = json.loads(auth_session)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': get_message('json_invalid', lang)}, status=400)
        
        print(f"[DEBUG] Verifying ChatGPT session...")
        
        # Остроумная проверка режимом
        result = check_chatgpt_session(auth_data)
        print(f"[DEBUG] check_chatgpt_session result: {result}")
        
        # Обработка результата
        if isinstance(result, dict) and result.get('status') == 'VALID':
            # Сессия валидна
            email = result.get('email', 'Unknown')
            plan = result.get('plan', 'Unknown')
            expires = result.get('expires', 'N/A')
            
            return JsonResponse({
                'status': 'success',
                'message': get_message('session_verified', lang, email=email, plan=plan),
                'user_email': email,
                'plan': plan,
                'expires': expires
            }, status=200)
        
        # Обработка ошибок
        error_messages = {
            'INVALID_JSON': 'json_invalid',
            'INVALID_FORMAT': 'json_invalid',
            'MISSING_DATA': 'missing_data',
            'INVALID_USER_DATA': 'invalid_user_data',
            'INVALID_ACCESS_TOKEN': 'invalid_access_token',
            'ACCESS_TOKEN_EXPIRED': 'token_expired',
            'USER_MISMATCH': 'user_mismatch',
            'EMAIL_MISMATCH': 'email_mismatch',
            'PLAN_MISMATCH': 'plan_mismatch',
            'PLAN_NOT_FREE': 'plan_not_free',
            'SESSION_EXPIRED': 'session_expired',
            'INVALID_EXPIRES_FORMAT': 'invalid_expires',
            'ACCOUNT_PROBLEM': 'account_problem',
        }
        
        if isinstance(result, str):
            msg_key = error_messages.get(result, 'json_invalid')
        else:
            msg_key = 'json_invalid'
        
        return JsonResponse({
            'status': 'error',
            'message': get_message(msg_key, lang)
        }, status=400)
        
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


@require_http_methods(["POST"])
def activate_key(request):
    """Активация ключа с AuthSession токеном"""
    
    try:
        data = json.loads(request.body)
        key = data.get('key', '').strip().upper()
        auth_session = data.get('auth_session', '').strip()
        lang = data.get('lang', 'EN')
        
        if not key:
            return JsonResponse({'status': 'error', 'message': get_message('key_required', lang)}, status=400)
        
        if not auth_session:
            return JsonResponse({'status': 'error', 'message': get_message('auth_required', lang)}, status=400)
        
        # Проверяем что это валидный JSON
        try:
            auth_data = json.loads(auth_session)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': get_message('json_invalid', lang)}, status=400)
        
        print(f"[DEBUG activate_key] Verifying ChatGPT session before activation...")
        
        # Острова проверка сессии ПЕРЕД активацией ключа
        result = check_chatgpt_session(auth_data)
        print(f"[DEBUG activate_key] check_chatgpt_session result: {result}")
        
        # Если сессия не валидна - блокируем активацию
        if not (isinstance(result, dict) and result.get('status') == 'VALID'):
            error_messages = {
                'INVALID_JSON': 'json_invalid',
                'INVALID_FORMAT': 'json_invalid',
                'MISSING_DATA': 'missing_data',
                'INVALID_USER_DATA': 'invalid_user_data',
                'INVALID_ACCESS_TOKEN': 'invalid_access_token',
                'ACCESS_TOKEN_EXPIRED': 'token_expired',
                'USER_MISMATCH': 'user_mismatch',
                'EMAIL_MISMATCH': 'email_mismatch',
                'PLAN_MISMATCH': 'plan_mismatch',
                'PLAN_NOT_FREE': 'plan_not_free',
                'SESSION_EXPIRED': 'session_expired',
                'INVALID_EXPIRES_FORMAT': 'invalid_expires',
                'ACCOUNT_PROBLEM': 'account_problem',
            }
            
            if isinstance(result, str):
                msg_key = error_messages.get(result, 'json_invalid')
            else:
                msg_key = 'json_invalid'
            
            error_msg = get_message(msg_key, lang)
            return JsonResponse({
                'status': 'error',
                'message': get_message('cannot_activate', lang, error=error_msg)
            }, status=400)
        
        # Гет аксесс токен для сохранения
        access_token = auth_data.get('accessToken', '').strip()

        # Активируем ключ
        try:
            # Передаем полный auth_session JSON
            result = activate_key_via_api(key, auth_session)
            
            if result == 'act':
                # Сохраняем в БД при успешной активации
                try:
                    # Создаем запись в БД
                    order = Order.objects.create(
                        key=key,
                        token=auth_session
                    )
                    
                    print(f"Order saved: {order.id} - Key: {key} - Time: {order.created_at}")
                except Exception as e:
                    print(f"Error saving order: {str(e)}")
                    # Не прерываем процесс, если не удалось сохранить в БД
                
                return JsonResponse({
                    'status': 'success',
                    'message': get_message('activation_success', lang)
                }, status=200)
            else:
                # result содержит сообщение об ошибке
                return JsonResponse({
                    'status': 'error',
                    'message': get_message('activation_error', lang)
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