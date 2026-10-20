from django.conf import settings
from django.db import models

# discovery/models.py
class Discovery(models.Model):
  discovery_date = models.DateField()
  # ...
class Discovery(models.Model):
  dinosaur = models.ForeignKey(
      'dinosaurs.Dinosaur',
      on_delete=models.CASCADE,
      related_name='discoveries'
  )
  location = models.CharField(max_length=255)
  discovery_date = models.DateField()
  discovered_by = models.CharField(max_length=255)
  description = models.TextField(blank=True, null=True)

  # Ensure null=True, blank=True are set!
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
    return f'Discovery of {self.dinosaur} at {self.location}'