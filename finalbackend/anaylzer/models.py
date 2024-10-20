from django.db import models
from django.contrib.auth.models import User

class Resume(models.Model):
    file = models.FileField(upload_to='resumes/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file.name

class MockInterview(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,default=None)
    name = models.CharField(max_length=20,default="")
    role = models.CharField(max_length=20,default="")
    questions = models.TextField()
    answers   = models.TextField(default="")
    review    = models.TextField(default="")
    rating    = models.CharField(max_length=20,default="")
    created_at = models.DateTimeField(auto_now_add=True)

