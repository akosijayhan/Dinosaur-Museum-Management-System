from django.db import models


class MapCoordinates(models.Model):
    room = models.OneToOneField(
        'room.Room',  # Must match 'rooms' in INSTALLED_APPS
        on_delete=models.CASCADE,
        related_name='map_info',
    )
    floor_level = models.IntegerField(default=1)

    @property
    def name(self):
        return self.room.name

    def __str__(self):
        return f'{self.name} (Floor {self.floor_level})'