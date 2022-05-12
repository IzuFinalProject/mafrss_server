from fcm_django.api.rest_framework import FCMDeviceAuthorizedViewSet
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import UserRecordView, UserList, UserNotificationView, UserMediaView,UserProfileView
from django.urls import path, include

app_name = 'api'
urlpatterns = [
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
    path('auth/user/', UserRecordView.as_view()),
    path('auth/userList/', UserList.as_view()),
    path('auth/user/file', UserMediaView.as_view()),
    path('auth/user/profile', UserProfileView.as_view()),
    path('notification/', UserNotificationView.as_view()),
    path('devices', FCMDeviceAuthorizedViewSet.as_view({'post': 'create'}), name='create_fcm_device'),
]
