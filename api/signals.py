from django.db.models.signals import post_save, post_delete  # Import a post_save signal when a user is created
from django.contrib.auth.models import User  # Import the built-in User model, which is a sender
from django.dispatch import receiver  # Import the receiver
from .models import Profile, FileModel
import os


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    user = User.objects.filter(id=instance.profile.user_id)
    instance.profile.email = user[0].email
    instance.profile.username = user[0].username
    instance.profile.save()


@receiver(post_delete, sender=FileModel)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)
