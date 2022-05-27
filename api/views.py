import json
from django.contrib.auth.models import User
from django.core import serializers
from django.http import JsonResponse, HttpResponse
from fcm_django.models import FCMDevice
from rest_framework import status, generics
from rest_framework.decorators import api_view, throttle_classes, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from rest_framework.views import APIView
from firebase_admin.messaging import Message, Notification
from .forms import FileForm
from .models import FileModel, NotificationModel, Profile
from .serlializers import UserSerializer, PictureSerializer, NotificationSerializer
import requests
import environ

env = environ.Env()
# reading .env file
environ.Env.read_env()


class UserList(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = UserSerializer


class TenPerMinuteUserThrottle(UserRateThrottle):
    rate = '10/minute'


@api_view(['GET', ])
# @throttle_classes([TenPerMinuteUserThrottle])
@permission_classes((AllowAny,))
def getNotfications(self):
    notifications = NotificationModel.objects.all()
    serializer = NotificationSerializer(notifications,  many=True) #type list
    if serializer is not None:
        return JsonResponse(
            serializer.data,
            status=status.HTTP_200_OK,
             safe=False)
    return JsonResponse(
        {
            "error": True,
            "error_msg": serializer.error_messages,
        },
        status=status.HTTP_400_BAD_REQUEST
    )


class UserNotificationView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [TenPerMinuteUserThrottle]

    def get(self, request):
        notifications = NotificationModel.objects.filter(user_id=request.user.id)
        serializer = NotificationSerializer(notifications, many=True)
        if notifications is not None:
            return JsonResponse(
                serializer.data,
                status=status.HTTP_200_OK,
             safe=False)
        return JsonResponse(
            {
                "error": True,
                "error_msg": serializer.error_messages,
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    def post(self, request):
        body = json.loads(request.body.decode('utf-8'))
        title = body['title']
        message = body['message']
        user = User.objects.filter(username=body['username'])
        NotificationModel(message=message, user_id=user[0].id, title=title).save()
        device = FCMDevice.objects.filter(user_id=user[0].id)
        try:
            device.send_message(Message(
                notification=Notification(
                    title,
                    body=message
                )))
            return JsonResponse({'status': "Notification is Sent"})
        except Exception as e:
            print(e)
            return JsonResponse(
                {
                    "error": True
                },
                status=status.HTTP_400_BAD_REQUEST
            )


class SecurityView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        RPI_URL = env("RPI_URL")
        body = json.loads(request.body.decode('utf-8'))
        headers = {'content-type': 'application/json'}
        if body['access'] and (body['access'] == "yes"):
            response = requests.post(RPI_URL + '/led', data=json.dumps({'led': 'on'}), headers=headers)
            if response.ok:
                return JsonResponse(
                    {
                        "message": "Accesses Granted Successfully"
                    },
                    status=status.HTTP_200_OK
                )
            else:
                return JsonResponse(
                    {
                        "error": True
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            response = requests.post(RPI_URL + '/led', data=json.dumps({'led': 'off'}), headers=headers)
            if response.ok:
                return JsonResponse(
                    {
                        "message": "Accesses Denied Successfully"
                    },
                    status=status.HTTP_200_OK
                )
            else:
                return JsonResponse(
                    {
                        "error": True
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )


class UserMediaView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        form = FileForm(request.POST, request.FILES)
        if form.is_valid():
            for f in request.FILES.getlist('file'):
                instance = FileModel(file=f, user=request.user)
                instance.save()
            return JsonResponse(status=status.HTTP_201_CREATED)
        return JsonResponse(
                    {
                        "message": "Accesses Denied Successfully"
                    },
            status=status.HTTP_400_BAD_REQUEST
        )

    def get(self, request):
        queryset = FileModel.objects.filter(user_id=request.user.id)
        serializer = PictureSerializer(queryset, many=True)
        if serializer is not None:
            return JsonResponse(serializer.data, status=status.HTTP_200_OK)
        return JsonResponse(
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
            return JsonResponse(
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
            return JsonResponse(
                json.loads(serializers.serialize("json", Profile.objects.filter(user_id=request.user.id))),
                status=status.HTTP_200_OK
            )
        else:
            return JsonResponse("Error", status=status.HTTP_400_BAD_REQUEST)


class UserRecordView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        if serializer is not None:
            return JsonResponse(
                serializer.data,
                status=status.HTTP_200_OK
            )
        return JsonResponse(
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
            return JsonResponse(
                json.loads(serializers.serialize("json", User.objects.filter(id=request.user.id))),
                status=status.HTTP_200_OK
            )
        else:
            return JsonResponse("Error", status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        id = body['id']
        try:
            User.objects.filter(pk__in = id).delete()
            return JsonResponse(
                {"detail":"The user is deleted"},
                status=status.HTTP_200_OK
            )       
        except User.DoesNotExist:
            return JsonResponse( {"detail":"User doesnot exist!s"}, status=status.HTTP_400_BAD_REQUEST)
            
            
