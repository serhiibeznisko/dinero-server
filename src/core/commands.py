from django.core.management.base import BaseCommand, CommandError
from django.conf import settings


class DevCommand(BaseCommand):
    help_text = 'Command that can be run in DEV environment only.'

    def check(self, *args, **kwargs):
        super().check(*args, **kwargs)

        if settings.DEBUG is not True:
            raise CommandError(
                'This command is protected against running it in a non-DEV environment. '
                'If you still want to run it, consider changing DEBUG setting to True.'
            )
