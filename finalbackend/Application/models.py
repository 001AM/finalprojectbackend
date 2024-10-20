from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date
from Joblistings.models import JobListing
class Application(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    job_listing = models.ForeignKey(JobListing, on_delete=models.CASCADE)
    application_date = models.DateField(default=timezone.now)
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)
    cover_letter = models.TextField(blank=True)

    class Meta:
        db_table = 'jobsearch__application'
        verbose_name = 'Application'
        verbose_name_plural = 'Applications'
        ordering = ['application_date']

    def __str__(self):
        return f'{self.user.username} - {self.job_listing.title}'
