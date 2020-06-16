import pytest

from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication

from accounts.models import User
from accounts.serializers.authentication import TokenObtainSerializer
from accounts.serializers.password import UpdatePasswordSerializer, ResetPasswordSerializer
from accounts.serializers.registration import EmailSerializer, ActivateAccountSerializer, CheckFieldTakenSerializer
from accounts.serializers.users import MeSerializer
from core.generators import fake, DEFAULT_USER_PASSWORD


@pytest.mark.django_db
class TestCaseTokenObtainSerializer:
    def test_get_token_for_user(self, user):
        serializer = TokenObtainSerializer(user)

        assert serializer.data['access']
        assert serializer.data['refresh']

    def test_access_token(self, user):
        serializer = TokenObtainSerializer(user)
        auth_backend = JWTAuthentication()
        access = auth_backend.get_validated_token(serializer.data['access'])

        assert auth_backend.get_user(access) == user

    def test_refresh_token(self, user):
        serializer = TokenObtainSerializer(user)

        assert RefreshToken(serializer.data['refresh']).access_token


@pytest.mark.django_db
class TestCaseUpdatePasswordSerializer:
    def test_empty_data(self, user):
        serializer = UpdatePasswordSerializer(user, data={})

        assert not serializer.is_valid()

    def test_old_password_incorrect(self, user):
        serializer = UpdatePasswordSerializer(user, data={
            'old_password': DEFAULT_USER_PASSWORD + '!',
            'new_password': DEFAULT_USER_PASSWORD + '@',
        })

        assert not serializer.is_valid()
        assert 'old_password' in serializer.errors

    def test_new_password_too_common(self, user):
        serializer = UpdatePasswordSerializer(user, data={
            'old_password': DEFAULT_USER_PASSWORD,
            'new_password': 'password',
        })

        assert not serializer.is_valid()
        assert 'new_password' in serializer.errors

    def test_new_password_entire_numeric(self, user):
        serializer = UpdatePasswordSerializer(user, data={
            'old_password': DEFAULT_USER_PASSWORD,
            'new_password': '123098456345',
        })

        assert not serializer.is_valid()
        assert 'new_password' in serializer.errors

    def test_update_password(self, user):
        serializer = UpdatePasswordSerializer(user, data={
            'old_password': DEFAULT_USER_PASSWORD,
            'new_password': DEFAULT_USER_PASSWORD + '!',
        })

        assert serializer.is_valid()
        assert not serializer.errors

        serializer.save()
        user.refresh_from_db()

        assert user.check_password(DEFAULT_USER_PASSWORD + '!')


@pytest.mark.django_db
class TestCaseResetPasswordSerializer:
    def test_empty_data(self, user):
        serializer = ResetPasswordSerializer(user, data={})

        assert not serializer.is_valid()

    def test_new_password_too_common(self, user):
        serializer = ResetPasswordSerializer(user, data={
            'old_password': DEFAULT_USER_PASSWORD,
            'new_password': 'password',
        })

        assert not serializer.is_valid()
        assert 'new_password' in serializer.errors

    def test_new_password_entire_numeric(self, user):
        serializer = UpdatePasswordSerializer(user, data={
            'old_password': DEFAULT_USER_PASSWORD,
            'new_password': '123098456345',
        })

        assert not serializer.is_valid()
        assert 'new_password' in serializer.errors


@pytest.mark.django_db
class TestCaseEmailSerializer:
    def test_empty_data(self):
        serializer = EmailSerializer(data={})

        assert not serializer.is_valid()

    def test_incorrect_email(self):
        serializer = EmailSerializer(data={
            'email': 'not_email',
        })

        assert not serializer.is_valid()
        assert 'email' in serializer.errors

    def test_empty_email(self):
        serializer = EmailSerializer(data={
            'email': '',
        })

        assert not serializer.is_valid()
        assert 'email' in serializer.errors

    def test_correct_email(self):
        serializer = EmailSerializer(data={
            'email': fake.safe_email(),
        })

        assert serializer.is_valid()


@pytest.mark.django_db
class TestCaseActivateAccountSerializer:
    def test_empty_data(self):
        serializer = ActivateAccountSerializer(data={})

        assert not serializer.is_valid()

    def test_empty_uidb64(self, user):
        serializer = ActivateAccountSerializer(data={
            'uidb64': '',
            'token': default_token_generator.make_token(user),
        })

        assert not serializer.is_valid()
        assert 'uidb64' in serializer.errors

    def test_empty_token(self, user):
        serializer = ActivateAccountSerializer(data={
            'uidb64': urlsafe_base64_encode(force_bytes(user.id)),
            'token': '',
        })

        assert not serializer.is_valid()
        assert 'token' in serializer.errors

    def test_correct_data(self, user):
        serializer = ActivateAccountSerializer(data={
            'uidb64': urlsafe_base64_encode(force_bytes(user.id)),
            'token': default_token_generator.make_token(user),
        })

        assert serializer.is_valid()


@pytest.mark.django_db
class TestCaseCheckFieldTakenSerializer:
    def test_empty_data(self):
        serializer = CheckFieldTakenSerializer(data={})

        assert not serializer.is_valid()

    def test_invalid_field_choice(self):
        serializer = CheckFieldTakenSerializer(data={
            'field': 'invalid_choice',
            'value': 'value',
        })

        assert not serializer.is_valid()
        assert 'field' in serializer.errors

    def test_write_only_fields(self, user):
        serializer = CheckFieldTakenSerializer(data={
            'field': 'email',
            'value': user.email,
        })

        assert serializer.is_valid()
        assert 'field' not in serializer.validated_data
        assert 'value' not in serializer.validated_data

    def test_read_only_fields(self, user):
        serializer = CheckFieldTakenSerializer(data={
            'taken': 'not_boolean',
            'field': 'email',
            'value': user.email,
        })

        assert serializer.is_valid()
        assert len(serializer.validated_data.keys()) == 1
        assert 'taken' in serializer.validated_data
        assert serializer.validated_data['taken'] != 'not_boolean'

    def test_email_taken(self, user):
        serializer = CheckFieldTakenSerializer(data={
            'field': 'email',
            'value': user.email,
        })

        assert serializer.is_valid()
        assert serializer.validated_data['taken'] is True

    def test_email_taken_by_inactive_user(self, user):
        user.is_active = False
        user.save()

        with pytest.raises(User.DoesNotExist):
            User.objects.get(id=user.id)

        serializer = CheckFieldTakenSerializer(data={
            'field': 'email',
            'value': user.email,
        })

        assert serializer.is_valid()
        assert serializer.validated_data['taken'] is True

    def test_email_not_taken(self):
        serializer = CheckFieldTakenSerializer(data={
            'field': 'email',
            'value': fake.safe_email(),
        })

        assert serializer.is_valid()
        assert serializer.validated_data['taken'] is False


@pytest.mark.django_db
class TestCaseMeSerializer:
    def test_empty_data(self):
        serializer = MeSerializer(data={})

        assert not serializer.is_valid()

    def test_incorrect_email(self):
        serializer = MeSerializer(data={
            'email': 'not_email',
        })

        assert not serializer.is_valid()
        assert 'email' in serializer.errors

    def test_email_taken(self, user):
        serializer = MeSerializer(data={
            'email': user.email,
            'password': DEFAULT_USER_PASSWORD,
        })

        assert not serializer.is_valid()
        assert str(serializer.errors['email'][0]) == 'Email is already taken.'

    def test_password_too_common(self):
        serializer = MeSerializer(data={
            'email': fake.safe_email(),
            'password': 'password',
        })

        assert not serializer.is_valid()
        assert 'password' in serializer.errors

    def test_password_entire_numeric(self):
        serializer = MeSerializer(data={
            'email': fake.safe_email(),
            'password': '123098456345',
        })

        assert not serializer.is_valid()
        assert 'password' in serializer.errors

    def test_read_only_fields(self):
        serializer = MeSerializer(data={
            'id': fake.pyint(),
            'is_staff': fake.boolean(),
            'is_superuser': fake.boolean(),
            'email': fake.safe_email(),
            'password': DEFAULT_USER_PASSWORD,
        })

        assert serializer.is_valid()
        assert len(serializer.validated_data.keys()) == 2
        assert 'id' not in serializer.validated_data
        assert 'is_staff' not in serializer.validated_data
        assert 'is_superuser' not in serializer.validated_data

    def test_update_protected_password(self, user):
        serializer = MeSerializer(user, data={
            'password': DEFAULT_USER_PASSWORD,
        }, partial=True)

        assert serializer.is_valid()

        serializer.save()
        user.refresh_from_db()

        assert user.password != DEFAULT_USER_PASSWORD

    def test_create_user(self):
        email = fake.safe_email()
        serializer = MeSerializer(data={
            'email': email,
            'password': DEFAULT_USER_PASSWORD,
        }, partial=True)

        assert serializer.is_valid()
        assert serializer.save()
        assert User.all.count() == 1

        user = User.all.get(email=email)

        assert user.check_password(DEFAULT_USER_PASSWORD)
