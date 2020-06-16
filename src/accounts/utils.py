from django.contrib.auth import tokens
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from django.utils.translation import ugettext as _
from rest_framework import exceptions
from rest_framework.generics import get_object_or_404

from .models import User


def get_user_uidb64_token(uidb64: str, token: str):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
    except Exception:
        raise exceptions.ParseError(_('Link is invalid or expired.'))

    if not isinstance(uid, str) or not uid.isdigit():
        raise exceptions.ParseError(_('Link is invalid or expired.'))

    user = get_object_or_404(User, id=uid)

    if not tokens.default_token_generator.check_token(user, token):
        raise exceptions.ParseError(_('Link is invalid or expired.'))

    return user
