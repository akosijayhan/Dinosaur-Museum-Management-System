from django.conf import settings
from django.db import models


class ExtinctionEvent(models.Model):
    name = models.CharField(max_length=150, unique=True)
    period = models.CharField(max_length=100)
    estimated_date = models.CharField(max_length=100, default='Unknown')
    cause = models.TextField(default='', blank=True)
    description = models.TextField(default='', blank=True)
    image = models.ImageField(upload_to='extinction/', blank=True, null=True)
    dinosaur = models.ForeignKey(
        'dinosaurs.Dinosaur',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='extinction_events',
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} ({self.period})'