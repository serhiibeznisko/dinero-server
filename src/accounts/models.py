import uuid

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from .managers import UserManager, UserManagerActive
from core.mixins import UpdateMixin
from core.models import CreatedUpdatedModel


class BaseUser(AbstractBaseUser):
    USERNAME_FIELD = 'email'

    is_staff = models.BooleanField(
        'Staff status', default=False,
        help_text='Designates whether the user can log into this admin site as staff user.')
    is_active = models.BooleanField(
        'Active status', default=True,
        help_text='Designates whether the user should be treated as active. Deselect instead of deleting the user.')
    is_email_verified = models.BooleanField(
        'Email verified', default=False,
        help_text='Designates whether the user has verified its email address.')
    email = models.EmailField(blank=False, unique=True)

    class Meta:
        abstract = True


class User(BaseUser, PermissionsMixin, CreatedUpdatedModel, UpdateMixin):
    all = UserManager()
    objects = UserManagerActive()

    # The field is used by REST framework to create jwt token.
    jwt_secret = models.UUIDField(default=uuid.uuid4)

    name = models.CharField(max_length=128)
