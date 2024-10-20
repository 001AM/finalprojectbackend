from . import views
from django.views.generic import TemplateView
from django.urls import path

app_name = 'analyzer'

urlpatterns = [
    path('', TemplateView.as_view(template_name='index.html'), name='index'),
    path('upload/', views.ResumeUploadView.as_view(), name='upload_resume'),
    path('mockinterview_data/', views.MockInterviewData.as_view(), name='mockinterview_data'),
    # path('ser/', ser.views, name='ser'),
]
