from django.db import models
from django.utils import timezone
import pytz

class Order(models.Model):
    key = models.CharField(max_length=255)
    token = models.TextField()  # Изменен на TextField для длинных токенов
    created_at = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.created_at:
            # UTC+5 (Ашхабад, Тошкент)
            utc_plus_5 = pytz.timezone('Asia/Tashkent')
            self.created_at = timezone.now().astimezone(utc_plus_5)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order {self.key} - {self.created_at}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'

class Key(models.Model):
    key = models.CharField(max_length=100, unique=True)
    TARIFF_CHOICES = [
        ('month', 'Month'),
        ('year', 'Year'),
    ]
    tariff = models.CharField(max_length=10, choices=TARIFF_CHOICES)
    is_used = models.BooleanField(default=False)

    def __str__(self):
        return self.key
    
class OrderKeyTg(models.Model):
    key = models.CharField(max_length=255)
    tg_id = models.CharField(max_length=255)
    created_at = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.created_at:
            # UTC+5 (Ашхабад, Тошкент)
            utc_plus_5 = pytz.timezone('Asia/Tashkent')
            self.created_at = timezone.now().astimezone(utc_plus_5)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"OrderKeyTg {self.key} - {self.created_at}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'OrderKeyTg'
        verbose_name_plural = 'OrderKeyTgs'