# Production Setup Guide

## What Was Done

### 1. ✅ Static Files Collection
- Ran `python manage.py collectstatic --noinput`
- All static files (CSS, JS, images) collected to: `staticfiles/`
- Total: 131 static files copied

### 2. ✅ Django Settings Updated
- **DEBUG**: Changed from `True` to `False`
- **ALLOWED_HOSTS**: Set to `['*']` (update for specific domains if needed)
- **STATIC_ROOT**: Set to `BASE_DIR / 'staticfiles'`
- **STATICFILES_DIRS**: Configured to include app static directories
- **SECRET_KEY**: Updated (change to a secure value in real production)

### 3. 📋 Security Settings (Optional)
Production security settings are commented in `settings.py`:
```python
# SECURE_SSL_REDIRECT = True
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True
# SECURE_HSTS_SECONDS = 31536000
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# SECURE_HSTS_PRELOAD = True
```

Uncomment these for HTTPS deployment.

## Directory Structure for Production

```
keyactivate/
├── keyactivate/          # Project settings
│   └── settings.py      # ✅ Updated
├── activator/           # Your app
│   ├── static/          # Source static files
│   │   ├── css/
│   │   ├── js/
│   │   └── img/
│   ├── templates/       # HTML templates
│   └── ...
├── staticfiles/         # ✅ Collected statics (serve via web server)
├── db.sqlite3           # Database
├── manage.py
└── .env                 # Environment variables
```

## Deployment Steps

### 1. Web Server Configuration
Configure your web server (Nginx/Apache) to:
- Serve static files from `staticfiles/` directory
- Route dynamic requests to Django

**Example Nginx Configuration:**
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    # Serve static files
    location /static/ {
        alias /path/to/keyactivate/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Proxy to Django
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 2. Environment Configuration
Update `ALLOWED_HOSTS` in `settings.py`:
```python
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']
```

### 3. Database Migration
```bash
python manage.py migrate
```

### 4. Update SECRET_KEY
Generate a new secure SECRET_KEY:
```python
# Generate with: python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
SECRET_KEY = 'your-new-secure-key-here'
```

### 5. SSL/TLS (HTTPS)
- Install SSL certificate
- Uncomment HTTPS security settings in `settings.py`
- Set `SECURE_SSL_REDIRECT = True`

### 6. Start Django
With Gunicorn:
```bash
pip install gunicorn
gunicorn keyactivate.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

Or with production server of choice.

## Important Checklist

- [ ] Update `ALLOWED_HOSTS` with actual domain(s)
- [ ] Generate new `SECRET_KEY` (don't use default)
- [ ] Set up `.env` file with sensitive vars if using environment variables
- [ ] Configure SSL/TLS certificate
- [ ] Set up web server to serve static files
- [ ] Run database migrations
- [ ] Test with DEBUG=False locally
- [ ] Enable HTTPS security settings when using HTTPS

## Testing Production Configuration

```bash
# Check configuration for production issues
python manage.py check --deploy

# Collect static files (already done, but can re-run)
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate
```

## Notes

- Static files are now collected to `staticfiles/` directory
- Django's development server is NOT suitable for production
- Use a production WSGI server (Gunicorn, uWSGI, etc.)
- Use a reverse proxy (Nginx, Apache, etc.) for static files
- Monitor disk space (database and uploads grow over time)
- Set up regular backups of `db.sqlite3`

## Troubleshooting

### Static files not loading
- Verify web server is configured to serve from `staticfiles/`
- Clear browser cache
- Re-run `python manage.py collectstatic --noinput`

### 404 errors for static files
- Check web server logs
- Verify `STATIC_ROOT` and `STATIC_URL` in settings
- Ensure web server user has read permissions on `staticfiles/`

### ALLOWED_HOSTS not set correctly
- Update `ALLOWED_HOSTS` in `settings.py`
- Include all domains that will access the site
- Test with different domain names

---

**Status**: ✅ Project ready for production deployment
