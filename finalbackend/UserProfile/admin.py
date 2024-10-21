from django.contrib import admin
from .models import UserProfile, UserCategory, UserConnection, Post

admin.site.register(UserProfile)
admin.site.register(UserCategory)
admin.site.register(UserConnection)
admin.site.register(Post)