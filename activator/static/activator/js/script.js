// ===== @morginfp Redeem — Interactive Logic =====

(function () {
    'use strict';

    // --- Mobile Optimizations ---
    // Prevent double-tap zoom on buttons
    let lastTouchEnd = 0;
    document.addEventListener('touchend', (e) => {
        const now = Date.now();
        if (now - lastTouchEnd <= 300) {
            e.preventDefault();
        }
        lastTouchEnd = now;
    }, false);

    // Add touch feedback to interactive elements
    const addTouchFeedback = (selector) => {
        document.querySelectorAll(selector).forEach(el => {
            el.addEventListener('touchstart', () => el.style.opacity = '0.8');
            el.addEventListener('touchend', () => el.style.opacity = '1');
        });
    };

    // Apply touch feedback to buttons and links
    addTouchFeedback('.btn, .icon-btn, .section-link');

    // --- State ---
    let currentStep = 1;
    let keyValidated = false;
    let authValidated = false;
    let validatedKey = '';
    let validatedAuthSession = '';

    // --- DOM References ---
    const themeToggle = document.getElementById('themeToggle');
    const iconSun = document.querySelector('.icon-sun');
    const iconMoon = document.querySelector('.icon-moon');

    const step1 = document.getElementById('step1');
    const step2 = document.getElementById('step2');
    const step3 = document.getElementById('step3');
    const line1 = document.getElementById('line1');
    const line2 = document.getElementById('line2');

    const section1 = document.getElementById('section1');
    const section2 = document.getElementById('section2');
    const section3 = document.getElementById('section3');

    const keyInput = document.getElementById('keyInput');
    const validateKeyBtn = document.getElementById('validateKeyBtn');
    const keyStatus = document.getElementById('keyStatus');
    const keyStatusText = document.getElementById('keyStatusText');

    const authTextarea = document.getElementById('authTextarea');
    const validateAuthBtn = document.getElementById('validateAuthBtn');
    const authStatus = document.getElementById('authStatus');
    const authStatusText = document.getElementById('authStatusText');

    const activateBtn = document.getElementById('activateBtn');
    const activationStatus = document.getElementById('activationStatus');
    const activationStatusText = document.getElementById('activationStatusText');
    const activateBtnLabel = activateBtn.querySelector('[data-i18n="activate"]');
    const activateBtnDefaultLabel = activateBtnLabel ? activateBtnLabel.textContent.trim() : 'Activate';
    const langBtn = document.getElementById('langBtn');

    const translations = {
        EN: {
            nav_redeem: 'Redeem',
            page_title: 'Redeem Key',
            page_subtitle: 'Safe and fast subscription activation service',
            section1_title: 'Enter and verify your Key',
            key_placeholder: 'Enter your activation key',
            validate: 'Validate',
            section2_title: 'Get AuthSession data',
            open_chatgpt: 'Open ChatGPT',
            open_auth: 'Open AuthSession Page',
            section2_desc: 'Open the page below, copy the full JSON content, then paste it and click validate.',
            auth_placeholder: 'Paste the full JSON from AuthSession page',
            activate: 'Activate',
            warning_note: 'After activation, try refreshing the target page multiple times. The page will refresh itself to update the subscription status.',
            footer_slogan: 'Fast & secure key activation',
            msg_key_required: 'Please enter a valid key.',
            msg_key_short: 'Key is too short. Please check and try again.',
            msg_key_ok: 'Key verified successfully! Proceed to step 2.',
            msg_key_fail: 'Key verification failed.',
            msg_server_error: 'Server error. Please try again.',
            msg_key_changed: 'Key changed. Please validate again.',
            msg_auth_required: 'Please paste your AuthSession JSON data.',
            msg_json_invalid: 'Invalid JSON format. Please copy the complete content.',
            msg_auth_invalid: 'Invalid ChatGPT token. Please copy from the AuthSession page.',
            msg_auth_ok: 'ChatGPT token verified! You can now activate.',
            msg_auth_fail: 'Token verification failed.',
            msg_auth_changed: 'AuthSession changed. Please validate again.',
            msg_activating: 'Activating...',
            msg_activating_wait: 'Activating... Please wait.',
            msg_activation_ok: 'Activation complete! Refresh the target page to see the changes.',
            msg_activation_fail: 'Failed to activate the key. Please try again.',
            msg_server_error_late: 'Server error. Please try again later.',
            msg_activated: 'Activated'
        },
        RU: {
            nav_redeem: 'Активировать',
            page_title: 'Активация ключа',
            page_subtitle: 'Безопасная и быстрая активация подписки',
            section1_title: 'Введите и проверьте ключ',
            key_placeholder: 'Введите ключ активации',
            validate: 'Проверить',
            section2_title: 'Получить AuthSession данные',
            open_chatgpt: 'Открыть ChatGPT',
            open_auth: 'Открыть AuthSession',
            section2_desc: 'Откройте страницу ниже, скопируйте полный JSON и вставьте его, затем нажмите Проверить.',
            auth_placeholder: 'Вставьте полный JSON со страницы AuthSession',
            activate: 'Активировать',
            warning_note: 'После активации попробуйте обновить страницу несколько раз. Страница обновит статус подписки.',
            footer_slogan: 'Быстрая и безопасная активация ключа',
            msg_key_required: 'Введите корректный ключ.',
            msg_key_short: 'Ключ слишком короткий. Проверьте и попробуйте снова.',
            msg_key_ok: 'Ключ подтвержден! Перейдите к шагу 2.',
            msg_key_fail: 'Проверка ключа не удалась.',
            msg_server_error: 'Ошибка сервера. Попробуйте снова.',
            msg_key_changed: 'Ключ изменен. Проверьте снова.',
            msg_auth_required: 'Вставьте JSON AuthSession.',
            msg_json_invalid: 'Неверный формат JSON. Скопируйте полный текст.',
            msg_auth_invalid: 'Неверный токен ChatGPT. Скопируйте со страницы AuthSession.',
            msg_auth_ok: 'Токен ChatGPT подтвержден! Можно активировать.',
            msg_auth_fail: 'Проверка токена не удалась.',
            msg_auth_changed: 'AuthSession изменен. Проверьте снова.',
            msg_activating: 'Активация...',
            msg_activating_wait: 'Активация... Подождите.',
            msg_activation_ok: 'Активация завершена! Обновите страницу, чтобы увидеть изменения.',
            msg_activation_fail: 'Не удалось активировать ключ. Попробуйте снова.',
            msg_server_error_late: 'Ошибка сервера. Попробуйте позже.',
            msg_activated: 'Активировано'
        },
        CN: {
            nav_redeem: '兑换',
            page_title: '兑换密钥',
            page_subtitle: '安全快速的订阅激活服务',
            section1_title: '输入并验证密钥',
            key_placeholder: '输入激活密钥',
            validate: '验证',
            section2_title: '获取 AuthSession 数据',
            open_chatgpt: '打开 ChatGPT',
            open_auth: '打开 AuthSession 页面',
            section2_desc: '打开下面页面，复制完整 JSON，然后粘贴并点击验证。',
            auth_placeholder: '粘贴 AuthSession 页面中的完整 JSON',
            activate: '激活',
            warning_note: '激活后请多次刷新目标页面，页面会自动更新订阅状态。',
            footer_slogan: '快速安全的密钥激活',
            msg_key_required: '请输入有效密钥。',
            msg_key_short: '密钥太短，请检查后重试。',
            msg_key_ok: '密钥验证成功！请进入第 2 步。',
            msg_key_fail: '密钥验证失败。',
            msg_server_error: '服务器错误，请重试。',
            msg_key_changed: '密钥已更改，请重新验证。',
            msg_auth_required: '请粘贴 AuthSession JSON 数据。',
            msg_json_invalid: 'JSON 格式无效，请复制完整内容。',
            msg_auth_invalid: 'ChatGPT 令牌无效，请从 AuthSession 页面复制。',
            msg_auth_ok: 'ChatGPT 令牌验证成功！现在可以激活。',
            msg_auth_fail: '令牌验证失败。',
            msg_auth_changed: 'AuthSession 已更改，请重新验证。',
            msg_activating: '激活中...',
            msg_activating_wait: '激活中...请稍候。',
            msg_activation_ok: '激活完成！请刷新目标页面查看变化。',
            msg_activation_fail: '激活失败，请重试。',
            msg_server_error_late: '服务器错误，请稍后再试。',
            msg_activated: '已激活'
        }
    };

    let activationState = 'idle';
    let currentLang = 'RU';

    function t(key) {
        const langSet = translations[currentLang] || translations.EN;
        return langSet[key] || translations.EN[key] || key;
    }

    function setActivateLabel(text) {
        if (activateBtnLabel) {
            activateBtnLabel.textContent = text;
        } else {
            activateBtn.textContent = text;
        }
    }

    function applyLanguage(lang) {
        currentLang = translations[lang] ? lang : 'EN';
        langBtn.textContent = currentLang;
        localStorage.setItem('lang', currentLang);

        document.documentElement.lang = currentLang === 'RU'
            ? 'ru'
            : (currentLang === 'CN' ? 'zh' : 'en');

        document.querySelectorAll('[data-i18n]').forEach((el) => {
            const key = el.getAttribute('data-i18n');
            el.textContent = t(key);
        });

        document.querySelectorAll('[data-i18n-placeholder]').forEach((el) => {
            const key = el.getAttribute('data-i18n-placeholder');
            el.setAttribute('placeholder', t(key));
        });

        if (activationState === 'loading') {
            setActivateLabel(t('msg_activating'));
        } else if (activationState === 'done') {
            setActivateLabel(t('msg_activated'));
        } else {
            setActivateLabel(t('activate'));
        }
    }

    // --- Theme Toggle ---
    function getTheme() {
        return document.documentElement.classList.contains('dark') ? 'dark' : 'light';
    }

    function setTheme(theme) {
        document.documentElement.classList.remove('light', 'dark');
        document.documentElement.classList.add(theme);
        document.documentElement.style.colorScheme = theme;
        document.cookie = 'theme=' + theme + ';path=/;max-age=31536000';
        updateThemeIcon(theme);
    }

    function updateThemeIcon(theme) {
        if (theme === 'dark') {
            iconSun.style.display = 'none';
            iconMoon.style.display = 'block';
        } else {
            iconSun.style.display = 'block';
            iconMoon.style.display = 'none';
        }
    }

    themeToggle.addEventListener('click', () => {
        const next = getTheme() === 'dark' ? 'light' : 'dark';
        setTheme(next);
    });

    // Initialize icon
    updateThemeIcon(getTheme());

    // --- Stepper Logic ---
    function updateStepper() {
        const steps = [step1, step2, step3];
        const lines = [line1, line2];
        const sections = [section1, section2, section3];

        steps.forEach((s, i) => {
            const num = i + 1;
            s.classList.remove('active', 'completed', 'inactive');
            if (num < currentStep) {
                s.classList.add('completed');
            } else if (num === currentStep) {
                s.classList.add('active');
            } else {
                s.classList.add('inactive');
            }
        });

        lines.forEach((l, i) => {
            const num = i + 1;
            l.classList.toggle('completed', num < currentStep);
        });

        sections.forEach((sec, i) => {
            const num = i + 1;
            sec.classList.toggle('disabled', num > currentStep);
        });

        activateBtn.disabled = !(keyValidated && authValidated);
        if (keyValidated && authValidated) {
            section3.classList.remove('disabled');
        }
    }

    // --- Show Status Message ---
    function showStatus(el, textEl, text, type) {
        el.classList.remove('success', 'error', 'show');
        textEl.textContent = text;

        const svgContent = type === 'success'
            ? '<polyline points="20 6 9 17 4 12"></polyline>'
            : '<line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line>';

        el.querySelector('svg').innerHTML = '<circle cx="12" cy="12" r="10"></circle>' + svgContent;

        void el.offsetWidth; // force reflow
        el.classList.add(type, 'show');
    }

    function clearStatus(el, textEl) {
        el.classList.remove('success', 'error', 'show');
        textEl.textContent = '';
        el.querySelector('svg').innerHTML = '<circle cx="12" cy="12" r="10"></circle>';
    }

    // --- Get CSRF Token ---
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // --- Key Validation ---
    validateKeyBtn.addEventListener('click', () => {
        const val = keyInput.value.trim();

        if (!val) {
            showStatus(keyStatus, keyStatusText, t('msg_key_required'), 'error');
            keyInput.focus();
            return;
        }

        if (val.length < 8) {
            showStatus(keyStatus, keyStatusText, t('msg_key_short'), 'error');
            return;
        }

        // Отправляем запрос на сервер для проверки ключа
        validateKeyBtn.disabled = true;
        validateKeyBtn.textContent = '...';

        fetch('/api/check-key/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ key: val, lang: currentLang })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'available') {
                keyValidated = true;
                validatedKey = val;  // Сохраняем валидный ключ
                showStatus(keyStatus, keyStatusText, t('msg_key_ok'), 'success');
                validateKeyBtn.textContent = t('validate');
                validateKeyBtn.disabled = false;

                if (currentStep < 2) currentStep = 2;
                updateStepper();
            } else {
                showStatus(keyStatus, keyStatusText, data.message || t('msg_key_fail'), 'error');
                validateKeyBtn.textContent = t('validate');
                validateKeyBtn.disabled = false;
            }
        })
        .catch(error => {
            showStatus(keyStatus, keyStatusText, t('msg_server_error'), 'error');
            validateKeyBtn.textContent = t('validate');
            validateKeyBtn.disabled = false;
            console.error('Error:', error);
        });
    });

    // Enter key to validate
    keyInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') validateKeyBtn.click();
    });

    keyInput.addEventListener('input', () => {
        const val = keyInput.value.trim();

        if (keyValidated && val !== validatedKey) {
            keyValidated = false;
            authValidated = false;
            validatedKey = '';
            validatedAuthSession = '';
            currentStep = 1;
            updateStepper();
            clearStatus(authStatus, authStatusText);
            clearStatus(activationStatus, activationStatusText);
            showStatus(keyStatus, keyStatusText, t('msg_key_changed'), 'error');
            activationState = 'idle';
            setActivateLabel(t('activate'));
            activateBtn.disabled = true;
        }
    });

    // --- Auth Validation ---
    validateAuthBtn.addEventListener('click', () => {
        const val = authTextarea.value.trim();

        if (!val) {
            showStatus(authStatus, authStatusText, t('msg_auth_required'), 'error');
            authTextarea.focus();
            return;
        }

        // Try to parse as JSON
        let authData;
        try {
            authData = JSON.parse(val);
        } catch {
            showStatus(authStatus, authStatusText, t('msg_json_invalid'), 'error');
            return;
        }

        // Проверяем что это токен ChatGPT (должен содержать accessToken и user)
        if (!authData.accessToken || !authData.user) {
            showStatus(authStatus, authStatusText, t('msg_auth_invalid'), 'error');
            return;
        }

        validateAuthBtn.disabled = true;
        validateAuthBtn.textContent = '...';

        // Проверяем реальный токен через ChatGPT API
        fetch('/api/verify-token/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ auth_session: val, lang: currentLang })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                authValidated = true;
                validatedAuthSession = val;
                showStatus(authStatus, authStatusText, data.message || t('msg_auth_ok'), 'success');
                validateAuthBtn.textContent = t('validate');
                validateAuthBtn.disabled = false;

                if (currentStep < 3) currentStep = 3;
                updateStepper();
            } else {
                showStatus(authStatus, authStatusText, data.message || t('msg_auth_fail'), 'error');
                validateAuthBtn.textContent = t('validate');
                validateAuthBtn.disabled = false;
            }
        })
        .catch(error => {
            showStatus(authStatus, authStatusText, t('msg_server_error'), 'error');
            validateAuthBtn.textContent = t('validate');
            validateAuthBtn.disabled = false;
            console.error('Error:', error);
        });
    });

    authTextarea.addEventListener('input', () => {
        const val = authTextarea.value.trim();

        if (authValidated && val !== validatedAuthSession) {
            authValidated = false;
            validatedAuthSession = '';
            currentStep = 2;
            updateStepper();
            clearStatus(activationStatus, activationStatusText);
            showStatus(authStatus, authStatusText, t('msg_auth_changed'), 'error');
            activationState = 'idle';
            setActivateLabel(t('activate'));
            activateBtn.disabled = true;
        }
    });

    // --- Activate ---
    activateBtn.addEventListener('click', () => {
        if (!keyValidated || !authValidated) return;

        activationState = 'loading';
        activateBtn.disabled = true;
        setActivateLabel(t('msg_activating'));
        showStatus(activationStatus, activationStatusText, t('msg_activating_wait'), 'success');

        // Отправляем запрос на активацию
        fetch('/api/activate-key/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                key: validatedKey,
                auth_session: validatedAuthSession,
                lang: currentLang
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                showStatus(
                    activationStatus,
                    activationStatusText,
                    data.message || t('msg_activation_ok'),
                    'success'
                );
                activationState = 'done';
                setActivateLabel(t('msg_activated'));
            } else {
                showStatus(
                    activationStatus,
                    activationStatusText,
                    data.message || t('msg_activation_fail'),
                    'error'
                );
                activationState = 'idle';
                setActivateLabel(t('activate'));
                activateBtn.disabled = false;
            }
        })
        .catch(error => {
            showStatus(
                activationStatus,
                activationStatusText,
                t('msg_server_error_late'),
                'error'
            );
            activationState = 'idle';
            setActivateLabel(t('activate'));
            activateBtn.disabled = false;
            console.error('Error:', error);
        });
    });

    // --- Language toggle ---
    const langs = ['RU', 'EN', 'CN'];
    const savedLang = localStorage.getItem('lang');
    if (savedLang && langs.includes(savedLang)) {
        currentLang = savedLang;
    }
    applyLanguage(currentLang);

    langBtn.addEventListener('click', () => {
        const nextIndex = (langs.indexOf(currentLang) + 1) % langs.length;
        applyLanguage(langs[nextIndex]);
    });

    // --- Initialize ---
    updateStepper();
})();
