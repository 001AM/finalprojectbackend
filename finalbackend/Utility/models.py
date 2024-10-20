from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date

class Category(models.Model):
    type = models.CharField(max_length=255, default='')

    class Meta:
        db_table = 'userprofile__category'
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['type']

    def __str__(self):
        return self.type
class Location(models.Model):
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    country = models.CharField(max_length=255)

    class Meta:
        db_table = 'jobsearch__location'
        verbose_name = 'Location'
        verbose_name_plural = 'Locations'
        ordering = ['city', 'state', 'country']

    def __str__(self):
        return f'{self.city}, {self.state}, {self.country}'
