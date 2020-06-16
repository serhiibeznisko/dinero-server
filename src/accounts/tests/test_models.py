import pytest

from django.db import transaction
from django.db.utils import IntegrityError

from accounts.models import User
from core.generators import fake, DEFAULT_USER_PASSWORD


@pytest.mark.django_db
class TestUserModel:
    def test_create_normal_user(self):
        user = User.objects.create_user(
            fake.safe_email(),
            DEFAULT_USER_PASSWORD,
        )

        assert user.is_staff is False
        assert user.is_superuser is False
        assert user.is_email_verified is False
        assert user.check_password(DEFAULT_USER_PASSWORD)
        assert User.all.count() == 1

    def test_create_superuser(self):
        user = User.objects.create_superuser(
            fake.safe_email(),
            DEFAULT_USER_PASSWORD,
        )

        assert user.is_staff is True
        assert user.is_superuser is True
        assert user.is_email_verified is False
        assert user.check_password(DEFAULT_USER_PASSWORD)
        assert User.all.count() == 1

    def test_create_user_email_not_unique(self, user):
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                User.objects.create_superuser(
                    user.email,
                    DEFAULT_USER_PASSWORD,
                )

        assert User.all.count() == 1

    def test_superuser_hidden(self, user):
        assert User.objects.count() == 1

        user.update(is_superuser=True)

        assert User.objects.count() == 0

    def test_staff_user_hidden(self, user):
        assert User.objects.count() == 1

        user.update(is_staff=True)

        assert User.objects.count() == 0

    def test_inactive_user_hidden(self, user):
        assert User.objects.count() == 1

        user.update(is_active=False)

        assert User.objects.count() == 0

    def test_managers_all(self, users):
        users[0].update(is_superuser=True)
        users[1].update(is_active=False)

        assert User.objects.count() == 1
        assert User.all.count() == 3

    def test_update(self, user):
        new_email = user.email + '@'
        user.update(email=new_email)
        user.refresh_from_db()

        assert user.email == new_email
