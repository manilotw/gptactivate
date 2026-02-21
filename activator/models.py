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