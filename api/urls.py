from fcm_django.api.rest_framework import FCMDeviceAuthorizedViewSet
from .views import UserRecordView, UserList, UserNotificationView, UserMediaView, UserProfileView, SecurityView, getNotfications
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
    path('notifications/', getNotfications),
    path('devices', FCMDeviceAuthorizedViewSet.as_view({'post': 'create'}), name='create_fcm_device'),
    path('security', SecurityView.as_view()),
]
