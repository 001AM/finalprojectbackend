######################EXTRA FUNCTION IMPORT##################################
import re
import os
import csv
import pytz
import json
import uuid
import hmac
import time
import base64
import asyncio
import hashlib
import requests
import websocket
import threading
from copy import deepcopy
from decimal import Decimal
from datetime import datetime, timedelta
from io import BytesIO
import secrets
import sys
import traceback
########################EXTRA DJANGO IMPORT###################################
from django.utils.timezone import now
from django.http import HttpResponse,JsonResponse
from django.core.mail import send_mail
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q, F, Count, Sum, Value, CharField, Subquery, OuterRef, ExpressionWrapper, IntegerField
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import connection, transaction,DatabaseError,IntegrityError
from django.utils import timezone
from django.core.serializers import serialize
from django.forms.models import model_to_dict
from django.db.models.functions import Concat, TruncDay, TruncMonth, ExtractHour, ExtractMonth, ExtractDay, ExtractYear
from django.core.files.base import ContentFile
from django.conf import settings
from django.utils.timezone import make_aware
from django.utils.dateparse import parse_date
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.shortcuts import get_object_or_404
from decimal import Decimal, InvalidOperation
from django.contrib.auth import authenticate, login
#######################REST_FRAMEWORK IMPORT#####################################
from rest_framework.decorators import *
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
#######################MODELS IMPORT#####################################
from django.contrib.auth.models import User
from .models import UserProfile, Post
#######################SERIALIZER IMPORT#####################################
from .serializers import UserSerializer,LoginSerializer,UserProfileUpdateSerializer, PostSerializer


# ##############################################################################################################################################
# Section: Registration
# ##############################################################################################################################################

@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([])
def signup_view(request):
    """
    API view for user registration.

    This endpoint allows users to register by providing their data. Upon successful
    registration, a JWT token pair (access and refresh tokens) is generated and returned.

    URL: `/signup/`
    Method: POST

    Request Data:
        - Expected: JSON object with user data, e.g., { "username": "user", "password": "pass" }

    Response:
        - On success: JSON object containing 'refresh' and 'access' tokens.
        - On failure: JSON object with validation errors.
    """
    if request.method == 'POST':
        reg_serializer = UserSerializer(data=request.data)
        if reg_serializer.is_valid():
            new_user = reg_serializer.save()

            # Generate JWT token for the newly created user
            refresh = RefreshToken.for_user(new_user)
            return JsonResponse({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        return JsonResponse(reg_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    return JsonResponse({'message': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([])
def login_view(request):
    """
    API view for user login.
    """
    if request.method == 'POST':
        print(request.data)
        serializer = LoginSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            user = serializer.validated_data
            # Generate JWT token for the authenticated user
            refresh = RefreshToken.for_user(user)
            return JsonResponse({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)

        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    return JsonResponse({'message': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([])
def logout_view(request):
    """
    API view for user logout.

    This endpoint allows users to log out by invalidating their refresh token. The token
    is blacklisted to prevent further use.

    URL: `/logout/`
    Method: POST

    Request Data:
        - Expected: JSON object with 'refresh_token', e.g., { "refresh_token": "your_refresh_token" }

    Response:
        - On success: JSON object with a logout success message.
        - On failure: JSON object with an error message.
    """
    try:
        refresh_token = request.data.get("refresh_token")
        token = RefreshToken(refresh_token)
        token.blacklist()
        return JsonResponse({'message': 'Logged out successfully'}, status=status.HTTP_200_OK)
    except Exception as e:
        return JsonResponse({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def update_user_profile(request):
    """
    API view for updating user profile.

    This endpoint allows authenticated users to update their profile information.

    URL: `/update-profile/`
    Method: PATCH

    Request Data:
        - Expected: JSON object with profile data fields to be updated, e.g., { "bio": "New bio", "website": "http://newwebsite.com" }

    Response:
        - On success: JSON object with updated profile data.
        - On failure: JSON object with validation errors or error message.
    """
    user = request.user

    try:
        user_profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        return JsonResponse({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = UserProfileUpdateSerializer(user_profile, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return JsonResponse(serializer.data, status=status.HTTP_200_OK)
    return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import UserConnection, User
from django.shortcuts import get_object_or_404
from .serializers import RelationSerializer
from django.contrib.auth.models import User

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def follow_user(request):
    follower_id = request.user.id  # Get the ID of the user
    following_id = request.data.get('following_id')  

    if not following_id:
        return Response({'message': 'Following ID is required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        following = User.objects.get(id=following_id)
    except User.DoesNotExist:
        return Response({'message': 'User Info does not exist'}, status=status.HTTP_404_NOT_FOUND)

    follower = User.objects.get(id=follower_id)  # Get the user instance using the ID

    if UserConnection.objects.filter(sender_user=follower, receiver_user=following).exists():
        return Response({'message': 'Already following this user'}, status=status.HTTP_400_BAD_REQUEST)

    connection = UserConnection.objects.create(sender_user=follower, receiver_user=following)

    serializer = RelationSerializer(connection)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def unfollow_user(request):
    follower = request.user.id
    following = request.data.get('following_id')
    connection = get_object_or_404(UserConnection, sender_user=follower, receiver_user=following)
    connection.delete()
    return Response({'message': 'User unfollowed successfully'}, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def follower_list(request):
    try:
        follower = request.user.id
        followers = UserConnection.objects.filter(sender_user=follower)
        serializer = RelationSerializer(followers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except UserConnection.DoesNotExist:
        return Response({'message': 'No connections found for the user'}, status=status.HTTP_404_NOT_FOUND) 
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_post(request):
    # Ensure the author is automatically set as the authenticated user
    data = request.data.copy()  # Create a mutable copy of request data
    data['author'] = request.user.id  # Set the author to the current logged-in user
    print(data)
    serializer = PostSerializer(data=data)
    if serializer.is_valid():
        serializer.save(author=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_posts(request):
    try:
        post_id = request.GET.get('id')
        user = request.user
        if post_id:
            posts = Post.objects.get(id=post_id)
            serializer = PostSerializer(posts)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            posts = Post.objects.filter(author=user).order_by('created_at')
            serializer = PostSerializer(posts, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
    except Post.DoesNotExist:
        return Response({'message': 'No posts found'}, status=status.HTTP_404_NOT_FOUND)