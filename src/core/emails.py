from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string


def send_templated_email(subject, context, template, recipient):
    body = render_to_string(
        template_name=f'emails/{template}.html',
        context=context,
    )

    if isinstance(recipient, str):
        recipient = [recipient]

    send_mail(
        subject=subject,
        message=body,
        html_message=body,
        from_email=settings.FROM_EMAIL,
        recipient_list=recipient,
    )
