from django.urls import path

from .views import authentication, users, registration, password

app_name = 'accounts'

urlpatterns = [
    path('me', users.MeAPIView.as_view()),
    path('users', users.UserListAPIView.as_view()),

    path('login', authentication.LoginAPIView.as_view()),
    path('token/refresh', authentication.RefreshTokenAPIView.as_view()),
    path('password', password.PasswordAPIView.as_view()),
    path('password/reset', password.ResetPasswordAPIView.as_view()),
    path('password/reset/send-email', password.SendResetEmailAPIView.as_view()),

    path('registration', registration.RegistrationAPIView.as_view()),
    path('registration/check-field-taken', registration.CheckFieldTakenAPIView.as_view()),
    path('registration/resend-email', registration.ResendEmailAPIView.as_view()),
    path('registration/activate-account', registration.ActivateAccountAPIView.as_view()),
]
