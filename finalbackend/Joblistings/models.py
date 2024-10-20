from django.db import models
from django.utils import timezone
from Utility.models import Location, Category
from CompanyProfile.models import Company

class JobListing(models.Model):
    title = models.CharField(max_length=255)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    description = models.TextField()
    requirements = models.TextField(blank=True)
    salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    posted_date = models.DateField(default=timezone.now)
    expiration_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'jobsearch__joblisting'
        verbose_name = 'Job Listing'
        verbose_name_plural = 'Job Listings'
        ordering = ['posted_date']

    def __str__(self):
        return self.title
