import json

from django.contrib.auth.models import User
from django.core import serializers
from django.http import JsonResponse, HttpResponse
from fcm_django.models import FCMDevice
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from firebase_admin.messaging import Message, Notification

from .forms import FileForm
from .models import FileModel, NotificationModel, Profile
from .serlializers import UserSerializer, PictureSerializer, NotificationSerializer


class UserList(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserNotificationView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        notfications = NotificationModel.objects.filter(user_id=request.user.id)
        serializer = NotificationSerializer(notfications, many=True)
        if notfications is not None:
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )
        return Response(
            {
                "error": True,
                "error_msg": serializer.error_messages,
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    def post(self, request):
        user_id = request.user.id
        device = FCMDevice.objects.filter(user_id=request.user)
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        title = body['title']
        message = body['message']
        instance = NotificationModel(message=message, user_id=user_id, title=title)
        instance.save()
        device.send_message(Message(
            notification=Notification(title, body=message,
                                      image="https://miro.medium.com/fit/c/176/176/1*fAmcI4p3jdeBDgL467AMGQ.jpeg")
        )
        )
        return JsonResponse({'status': "Notification is Sent"})


class UserMediaView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        form = FileForm(request.POST, request.FILES)
        if form.is_valid():
            for f in request.FILES.getlist('file'):
                instance = FileModel(file=f, user=request.user)
                instance.save()
            return Response(status=status.HTTP_201_CREATED)
        return Response(
            {
                "error": True,
                "error_msg": form.errors,
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    def get(self, request):
        queryset = FileModel.objects.filter(user_id=request.user.id)
        serializer = PictureSerializer(queryset, many=True)
        if serializer is not None:
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(
            {
                "error": True,
                "error_msg": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST
        )


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_pref = Profile.objects.filter(user_id=request.user.id)
        if user_pref is not None:
            return HttpResponse(serializers.serialize('json', user_pref), content_type="application/json");
        else:
            return Response(
                {
                    "error": True
                },
                status=status.HTTP_400_BAD_REQUEST
            )

    def put(self, request, *args, **kwargs):
        user_pref = Profile.objects.filter(user_id=request.user.id)
        user = User.objects.filter(id=request.user.id)
        if request.data.get('email'):
            user_pref.update(email=request.data.get('email'))
            user.update(email=request.data.get('email'))
        if request.data.get('first_name'):
            user_pref.update(first_name=request.data.get('first_name'))
            user.update(first_name=request.data.get('first_name'))
        if request.data.get('last_name'):
            user_pref.update(last_name=request.data.get('last_name'))
            user.update(last_name=request.data.get('last_name'))
        if user_pref is not None:
            return Response(
                json.loads(serializers.serialize("json", Profile.objects.filter(user_id=request.user.id))),
                status=status.HTTP_200_OK
            )
        else:
            return Response("Error", status=status.HTTP_400_BAD_REQUEST)


class UserRecordView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        if serializer is not None:
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )
        return Response(
            {
                "error": True,
                "error_msg": serializer.error_messages,
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    def put(self, request, *args, **kwargs):
        user = User.objects.filter(id=request.user.id)
        if request.data.get('email'):
            user.update(email=request.data.get('email'))
        if request.data.get('username'):
            user.update(username=request.data.get('username'))
        if user is not None:
            return Response(
                json.loads(serializers.serialize("json", User.objects.filter(id=request.user.id))),
                status=status.HTTP_200_OK
            )
        else:
            return Response("Error", status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, format=None):
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        user_id = body['user_id']
        user = User.objects.filter(id=user_id)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
