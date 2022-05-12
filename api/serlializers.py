from abc import ABC

from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from .models import FileModel, NotificationModel


class PictureSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileModel
        fields = ('user', 'file')


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationModel
        fields = ('message', 'title', 'created_at','id')


class UserSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'is_superuser',
            'email',
            'first_name',
            'last_name',
            'date_joined',
        )
        validators = [
            UniqueTogetherValidator(
                queryset=User.objects.all(),
                fields=['username', 'email']
            )
        ]
