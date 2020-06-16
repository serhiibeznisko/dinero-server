from django.db import models

from core.utils import update_fk_multiple


class UpdateMixin:
    """ Mixin to update model fields that are passed in kwargs. """

    def update(self, save=True, **kwargs):
        if self._state.adding:
            raise self.DoesNotExist
        for key, value in kwargs.items():
            setattr(self, key, value)
        if save:
            self.save(update_fields=kwargs.keys())


class UpdateM2MMixin:
    """ Mixin to update m2m model relations. """

    def update_m2m(self, **kwargs):
        if self._state.adding:
            raise self.DoesNotExist
        for field, items in kwargs.items():
            if items is not None:
                getattr(self, field).set(items)


class UpdateForeignKeyItemsMixin:
    """ Add update_fk_items method to model that performs bulk update_fk_multiple. """

    def update_fk_items(self, items):
        for field_name, field_values, field_key in items:
            if field_values is not None:
                update_fk_multiple(self, field_name, field_values, field_key)


class ManagerActive(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)
