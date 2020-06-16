import pytest
import uuid
from freezegun import freeze_time

from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed, InvalidToken
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import User
from core.generators import fake, DEFAULT_USER_PASSWORD
from core.tests import test_error_response

BASE_URL = '/api/v1/accounts/'
ME_URL = BASE_URL + 'me'
LOGIN_URL = BASE_URL + 'login'
TOKEN_REFRESH_URL = BASE_URL + 'token/refresh'
PASSWORD_URL = BASE_URL + 'password'
PASSWORD_RESET_URL = BASE_URL + 'password/reset'
PASSWORD_RESET_EMAIL_URL = BASE_URL + 'password/reset/send-email'
REGISTRATION_URL = BASE_URL + 'registration'
CHECK_FIELD_TAKEN_URL = BASE_URL + 'registration/check-field-taken'
REGISTRATION_RESEND_EMAIL_URL = BASE_URL + 'registration/resend-email'
ACTIVATE_ACCOUNT_URL = BASE_URL + 'registration/activate-account'


@pytest.mark.django_db
class TestMeView:
    def test_no_credentials(self, client):
        response = client.get(ME_URL)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data == test_error_response('Authentication credentials were not provided.')

    def test_get_inactive_account(self, authorised_client):
        authorised_client.user.update(is_active=False)
        response = authorised_client.get(ME_URL)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data == test_error_response('User not found')

    def tes_get_me(self, authorised_client):
        response = authorised_client.get(ME_URL)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == authorised_client.user.id


@pytest.mark.django_db
class TestLoginView:
    def test_without_credentials(self, client):
        response = client.post(LOGIN_URL)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data == test_error_response({
            'email': 'This field is required.',
            'password': 'This field is required.',
        })

    def test_invalid_credentials(self, client, user):
        response = client.post(LOGIN_URL, {
            'email': user.email + 'a',
            'password': DEFAULT_USER_PASSWORD,
        })

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data == test_error_response('No active account found with the given credentials')

    def test_access_token(self, client, user):
        response = client.post(LOGIN_URL, {
            'email': user.email,
            'password': DEFAULT_USER_PASSWORD,
        })

        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data

        auth_backend = JWTAuthentication()
        access = auth_backend.get_validated_token(response.data['access'])

        assert auth_backend.get_user(access) == user

    def test_access_token_after_expiration(self, client, user):
        time1, time2 = '2100-01-01 00:00:00', '2100-01-02 00:00:01'

        with freeze_time(time1):
            response = client.post(LOGIN_URL, {
                'email': user.email,
                'password': DEFAULT_USER_PASSWORD,
            })

        assert response.status_code == status.HTTP_200_OK

        with freeze_time(time2):
            auth_backend = JWTAuthentication()
            with pytest.raises(InvalidToken):
                auth_backend.get_validated_token(response.data['access'])


@pytest.mark.django_db
class TestRefreshTokenView:
    def test_refresh_without_token(self, client):
        response = client.post(TOKEN_REFRESH_URL)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data == test_error_response({
            'refresh': 'This field is required.',
        })

    def test_refresh_with_invalid_refresh_token(self, client):
        response = client.post(TOKEN_REFRESH_URL, {
            'refresh': 'invalid_token',
        })

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data == test_error_response('Token is invalid or expired')

    def test_refresh_with_access_token(self, client, access_token):
        response = client.post(TOKEN_REFRESH_URL, {
            'refresh': access_token,
        })

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data == test_error_response('Token has wrong type')

    def test_refresh_token(self, client, user):
        refresh_token = str(RefreshToken.for_user(user))
        response = client.post(TOKEN_REFRESH_URL, {
            'refresh': refresh_token,
        })

        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data

        auth_backend = JWTAuthentication()
        access = auth_backend.get_validated_token(response.data['access'])

        assert auth_backend.get_user(access) == user

    def test_refresh_token_after_changing_jwt_secret(self, client, user):
        refresh_token = str(RefreshToken.for_user(user))
        user.update(jwt_secret=uuid.uuid4())
        response = client.post(TOKEN_REFRESH_URL, {
            'refresh': refresh_token,
        })

        assert response.status_code == status.HTTP_200_OK

        auth_backend = JWTAuthentication()
        access = auth_backend.get_validated_token(response.data['access'])

        with pytest.raises(AuthenticationFailed):
            auth_backend.get_user(access)

    def test_refresh_before_expiration(self, client, user):
        time1, time2 = '2100-01-01 00:00:00', '2100-01-07 23:59:59'

        with freeze_time(time1):
            refresh_token = str(RefreshToken.for_user(user))

        with freeze_time(time2):
            response = client.post(TOKEN_REFRESH_URL, {
                'refresh': refresh_token,
            })

        assert response.status_code == status.HTTP_200_OK

    def test_refresh_with_expired_token(self, client, user):
        time1, time2 = '2100-01-01 00:00:00', '2100-01-08 00:00:01'

        with freeze_time(time1):
            refresh_token = str(RefreshToken.for_user(user))

        with freeze_time(time2):
            response = client.post(TOKEN_REFRESH_URL, {
                'refresh': refresh_token,
            })

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data == test_error_response('Token is invalid or expired')


@pytest.mark.django_db
class TestPasswordView:
    def test_change_password_with_invalid_old_password(self, authorised_client):
        response = authorised_client.put(PASSWORD_URL, {
            'old_password': DEFAULT_USER_PASSWORD + '!',
            'new_password': DEFAULT_USER_PASSWORD + 'a',
        })

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data == test_error_response({
            'old_password': 'Old password is incorrect.',
        })

    def test_change_password(self, authorised_client):
        new_password = DEFAULT_USER_PASSWORD + 'a'
        response = authorised_client.put(PASSWORD_URL, {
            'old_password': DEFAULT_USER_PASSWORD,
            'new_password': new_password,
        })

        assert response.status_code == status.HTTP_200_OK

        user = authorised_client.user
        user.refresh_from_db()

        assert user.check_password(new_password)


@pytest.mark.django_db
class TestResetPasswordView:
    def test_empty_data(self, client):
        response = client.post(PASSWORD_RESET_URL)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data == test_error_response({
            'uidb64': 'This field is required.',
            'token': 'This field is required.',
            'new_password': 'This field is required.',
        })

    def test_invalid_uidb64(self, client):
        response = client.post(PASSWORD_RESET_URL, {
            'token': 'incorrect_token',
            'uidb64': 'incorrect_uidb64',
            'new_password': DEFAULT_USER_PASSWORD,
        })

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data == test_error_response('Link is invalid or expired.')

    def test_invalid_uid(self, client, user):
        response = client.post(PASSWORD_RESET_URL, {
            'token': 'invalid_token',
            'uidb64': urlsafe_base64_encode(force_bytes(user.id)),
            'new_password': DEFAULT_USER_PASSWORD,
        })

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data == test_error_response('Link is invalid or expired.')

    def test_invalid_user_id(self, client):
        response = client.post(PASSWORD_RESET_URL, {
            'token': 'incorrect_token',
            'uidb64': urlsafe_base64_encode(force_bytes(888)),
            'new_password': DEFAULT_USER_PASSWORD,
        })

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data == test_error_response('No User matches the given query.')

    def test_another_user_token(self, client, users):
        response = client.post(PASSWORD_RESET_URL, {
            'token': default_token_generator.make_token(users[0]),
            'uidb64': urlsafe_base64_encode(force_bytes(users[1].id)),
            'new_password': DEFAULT_USER_PASSWORD,
        })

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data == test_error_response('Link is invalid or expired.')

    def test_reset_password(self, client, user):
        new_password = DEFAULT_USER_PASSWORD + 'a'
        response = client.post(PASSWORD_RESET_URL, {
            'token': default_token_generator.make_token(user),
            'uidb64': urlsafe_base64_encode(force_bytes(user.id)),
            'new_password': new_password,
        })

        assert response.status_code == status.HTTP_204_NO_CONTENT

        user.refresh_from_db()

        assert user.check_password(new_password)
        assert not user.check_password(DEFAULT_USER_PASSWORD)


@pytest.mark.django_db
class TestRegistrationView:
    def test_empty_data(self, client):
        response = client.post(REGISTRATION_URL)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data == test_error_response({
            'email': 'This field is required.',
            'password': 'This field is required.',
        })

    def test_register_email_taken(self, client, user):
        response = client.post(REGISTRATION_URL, {
            'email': user.email,
            'password': DEFAULT_USER_PASSWORD,
        })

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data == test_error_response({'email': 'Email is already taken.'})

    @pytest.mark.parametrize('password, expected_response', [
        (
                'short',
                test_error_response({'password': 'This password is too short. It must contain at least 8 characters.'}),
        ),
        (
                '123456789513241241234',
                test_error_response({'password': 'This password is entirely numeric.'}),
        ),
        (
                'qwerty123',
                test_error_response({'password': 'This password is too common.'}),
        ),
    ])
    def test_register_wrong_password(self, password, expected_response, client):
        response = client.post(REGISTRATION_URL, {
            'email': fake.safe_email(),
            'password': password,
        })

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data == expected_response

    def test_register(self, client):
        email = fake.safe_email()
        response = client.post(REGISTRATION_URL, {
            'email': email,
            'password': DEFAULT_USER_PASSWORD,
        })

        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data

        user = User.all.get(email=email)

        assert user.check_password(DEFAULT_USER_PASSWORD)
        assert not user.is_email_verified

    def test_register_with_read_only_fields(self, client):
        email = fake.safe_email()
        response = client.post(REGISTRATION_URL, {
            'id': 0,
            'is_staff': True,
            'is_superuser': True,
            'email': email,
            'password': DEFAULT_USER_PASSWORD,
        })

        user = User.all.get(email=email)

        assert response.status_code == status.HTTP_200_OK
        assert user.id != 0
        assert not user.is_staff
        assert not user.is_superuser


@pytest.mark.django_db
class TestCheckFieldTakenView:
    def test_invalid_field(self, client):
        response = client.post(CHECK_FIELD_TAKEN_URL, {
            'field': 'invalid_field',
            'value': fake.safe_email(),
        })

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data == test_error_response({'field': '"invalid_field" is not a valid choice.'})

    def test_email_taken(self, client, user):
        response = client.post(CHECK_FIELD_TAKEN_URL, {
            'field': 'email',
            'value': user.email,
        })

        assert response.status_code == status.HTTP_200_OK
        assert response.data == {'taken': True}

    def test_email_not_taken(self, client):
        response = client.post(CHECK_FIELD_TAKEN_URL, {
            'field': 'email',
            'value': fake.safe_email(),
        })

        assert response.status_code == status.HTTP_200_OK
        assert response.data == {'taken': False}


@pytest.mark.django_db
class TestActivateAccountView:
    def test_empty_data(self, client):
        response = client.post(ACTIVATE_ACCOUNT_URL)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data == test_error_response({
            'uidb64': 'This field is required.',
            'token': 'This field is required.',
        })

    def test_invalid_uidb64(self, client):
        response = client.post(ACTIVATE_ACCOUNT_URL, {
            'token': 'incorrect_token',
            'uidb64': 'incorrect_uidb64',
        })

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data == test_error_response('Link is invalid or expired.')

    def test_invalid_uid(self, client, user):
        user.update(is_email_verified=False)
        response = client.post(ACTIVATE_ACCOUNT_URL, {
            'token': 'invalid_token',
            'uidb64': urlsafe_base64_encode(force_bytes(user.id)),
        })
        user.refresh_from_db()

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data == test_error_response('Link is invalid or expired.')
        assert not user.is_email_verified

    def test_invalid_user_id(self, client):
        response = client.post(ACTIVATE_ACCOUNT_URL, {
            'token': 'incorrect_token',
            'uidb64': urlsafe_base64_encode(force_bytes(888)),
        })

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data == test_error_response('No User matches the given query.')

    def test_another_user_token(self, client, users):
        users[0].update(is_email_verified=False)
        users[1].update(is_email_verified=False)
        response = client.post(ACTIVATE_ACCOUNT_URL, {
            'token': default_token_generator.make_token(users[0]),
            'uidb64': urlsafe_base64_encode(force_bytes(users[1].id)),
        })

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data == test_error_response('Link is invalid or expired.')

    def test_activate_account(self, client, user):
        user.update(is_email_verified=False)
        response = client.post(ACTIVATE_ACCOUNT_URL, {
            'token': default_token_generator.make_token(user),
            'uidb64': urlsafe_base64_encode(force_bytes(user.id)),
        })
        user.refresh_from_db()

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert user.is_email_verified
