from django.db import models
from django.contrib.auth.models import User


# Create your models here.

def get_upload_path(instance, filename):
    return 'files/{0}/{1}'.format(instance.user.username, filename)


class FileModel(models.Model):
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to=get_upload_path)
    user = models.OneToOneField(User, on_delete=models.CASCADE)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=256, default=None, blank=True, null=True)
    last_name = models.CharField(max_length=256, default=None, blank=True, null=True)
    username = models.CharField(max_length=256, default=None, blank=True, null=True)
    email = models.CharField(max_length=256, default=None, blank=True, null=True)

    def __str__(self):
        return str(self.user.usrename)


class NotificationModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=100, default='title')
    message = models.CharField(max_length=100, default='message')
    user_id = models.IntegerField(default=0)

    class Meta:
        ordering = ['created_at']
