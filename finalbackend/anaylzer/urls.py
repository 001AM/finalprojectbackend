from .views import ResumeUploadView
from django.views.generic import TemplateView
from django.urls import path

app_name = 'analyzer'

urlpatterns = [
    path('', TemplateView.as_view(template_name='index.html'), name='index'),
    path('upload/', ResumeUploadView.as_view(), name='upload_resume'),
    # path('ser/', ser.views, name='ser'),
]
