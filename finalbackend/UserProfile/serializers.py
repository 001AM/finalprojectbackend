from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.exceptions import ValidationError
from .models import UserProfile, UserConnection, Post

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'username', 'password')

    def create(self, validated_data):
        email = validated_data.get('email')
        username = validated_data.get('username')
        password = validated_data.get('password')
        if not email:
            raise ValueError(_('The Email must be set'))
        user = User(email=email, username=username)
        user.set_password(password)  # Set the password using set_password method
        user.is_active= True
        user.save()
        UserProfile.objects.create(user=user)
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            raise serializers.ValidationError("Both username and password are required.")

        user = authenticate(username=username, password=password)
        if user is None:
            raise serializers.ValidationError("Invalid credentials. Please try again.")

        if not user.is_active:
            raise serializers.ValidationError("User account is not active.")

        return user


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['profile_picture', 'date_of_birth', 'bio', 'website', 'location', 'gender']
        extra_kwargs = {
            'profile_picture': {'required': False},
            'date_of_birth': {'required': False},
            'bio': {'required': False},
            'website': {'required': False},
            'location': {'required': False},
            'gender': {'required': False},
        }


class RelationSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserConnection
        fields = '__all__'

class PostSerializer(serializers.ModelSerializer):
    total_likes = serializers.SerializerMethodField()  # To calculate the total likes

    class Meta:
        model = Post
        fields = ['id', 'author', 'title', 'content', 'image', 'created_at', 'updated_at', 'published_at', 'is_published', 'total_likes']
        read_only_fields = ['author', 'created_at', 'updated_at', 'total_likes']  # These fields will not be set by the user

    def get_total_likes(self, obj):
        return obj.likes.count()