from django.conf import settings
from django.db import models


class Room(models.Model):
    name = models.CharField(max_length=100, unique=True)
    floor = models.IntegerField(default=1)
    description = models.TextField(default='', blank=True)
    image = models.ImageField(upload_to='rooms/', blank=True, null=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['floor', 'name']

    def __str__(self):
        return f'{self.name} (Floor {self.floor})'