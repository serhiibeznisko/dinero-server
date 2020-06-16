from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from core.emails import send_templated_email


def generate_web_app_link(request, user, view_name):
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    return request.build_absolute_uri(reverse(view_name, args=(uidb64, token)))


def send_activation_email(request, user):
    pass
    # subject = 'Activate your account.'
    # context = {
    #     'link': generate_web_app_link(request, user, 'accounts:activate-account'),
    # }
    # template = 'activate_account'
    # send_templated_email(subject, context, template, user.email)


def send_reset_email(request, user):
    pass
    # subject = 'Reset your password.'
    # context = {
    #     'link': generate_web_app_link(request, user, 'accounts:reset-password'),
    # }
    # template = 'reset_password'
    # send_templated_email(subject, context, template, user.email)
