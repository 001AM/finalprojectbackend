from django.db import models
from django.utils import timezone
from datetime import date
from django.contrib.auth.models import User
from Utility.models import Category

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    date_of_birth = models.DateField(null=True, blank=True)
    bio = models.TextField(null=True,blank=True, max_length=500)
    website = models.URLField(null=True,blank=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    gender = models.CharField(max_length=10, choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')], blank=True, null=True)

    class Meta:
        db_table = 'userprofile__userprofile'
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
        ordering = ['user__username']

    def __str__(self):
        return f'{self.user.username} Profile'

    def get_full_name(self):
        return f'{self.user.first_name} {self.user.last_name}'

    def get_age(self):
        if self.date_of_birth:
            today = date.today()
            return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        return None

    def get_profile_picture_url(self):
        if self.profile_picture:
            return self.profile_picture.url
        return '/static/default_profile_pic.jpg'

    def is_birthday_today(self):
        if self.date_of_birth:
            today = timezone.now().date()
            return today.month == self.date_of_birth.month and today.day == self.date_of_birth.day
        return False

class UserCategory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ManyToManyField(Category)

    class Meta:
        db_table = 'userprofile__usercategory'
        verbose_name = 'User Category'
        verbose_name_plural = 'User Categories'
        ordering = ['user']

    def __str__(self):
        return f'{self.user.username} - Categories'
