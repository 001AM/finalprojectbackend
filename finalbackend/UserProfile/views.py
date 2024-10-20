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
from .models import UserProfile
#######################SERIALIZER IMPORT#####################################
from .serializers import UserSerializer,LoginSerializer,UserProfileUpdateSerializer


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
