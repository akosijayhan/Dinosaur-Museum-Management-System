from django.conf import settings
from django.db import models


class Dinosaur(models.Model):
  name = models.CharField(max_length=100)
  species = models.CharField(max_length=100)
  period = models.CharField(max_length=100)
  diet = models.CharField(max_length=50)
  description = models.TextField(blank=True, null=True)
  image = models.ImageField(upload_to='dinosaurs/', blank=True, null=True)
  room = models.ForeignKey(
      'room.Room',
      on_delete=models.SET_NULL,
      null=True,
      blank=True,
      related_name='dinosaurs',
  )
  created_by = models.ForeignKey(
      settings.AUTH_USER_MODEL,
      on_delete=models.SET_NULL,
      null=True,
      blank=True,
  )
  created_at = models.DateTimeField(auto_now_add=True)

  def __str__(self):
    return self.name