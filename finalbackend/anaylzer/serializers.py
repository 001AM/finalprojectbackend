from rest_framework import serializers
from .models import Resume,MockInterview

class ResumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resume
        fields = '__all__'

class MockInterviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = MockInterview
        exclude = ['questions','answers']
