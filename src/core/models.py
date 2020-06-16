from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _


class CreatedUpdatedModel(models.Model):
    created_at = models.DateTimeField(_('Created at'), default=timezone.now)
    updated_at = models.DateTimeField(_('Last updated at'), auto_now=True)

    class Meta:
        abstract = True
