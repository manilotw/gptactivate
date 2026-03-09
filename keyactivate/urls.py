"""keyactivate URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from activator.views import index, check_key_status, activate_key, verify_chatgpt_token, check_subscription_plan

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='index'),
    path('api/check-key/', check_key_status, name='check_key_status'),
    path('api/verify-token/', verify_chatgpt_token, name='verify_chatgpt_token'),
    path('api/check-plan/', check_subscription_plan, name='check_subscription_plan'),
    path('api/activate-key/', activate_key, name='activate_key'),
]
