from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):
    """ Basic Manager for `User` model. It provides `create_user` and `create_superuser` methods. """

    use_in_migrations = True

    def _create_user(self, email, password, **kwargs):
        """ Create and save a User with the given email and password. """
        if not email:
            raise ValueError('Email is required.')
        if not password:
            raise ValueError('Password is required.')

        email = self.normalize_email(email).lower()
        user = self.model(email=email, **kwargs)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password, **kwargs):
        kwargs.setdefault('is_superuser', False)

        return self._create_user(email, password, **kwargs)

    def create_superuser(self, email, password, **kwargs):
        kwargs.setdefault('is_staff', True)
        kwargs.setdefault('is_superuser', True)

        return self._create_user(email, password, **kwargs)

    def get_queryset(self):
        return super().get_queryset()


class UserManagerActive(UserManager):
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True, is_superuser=False, is_staff=False)
