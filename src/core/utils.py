def get_or_create_m2m(instance, m2m_name, items, **kwargs):
    """ Helper method which extract model after m2m_name, then gets or creates new instance for every item
    in items list. Finally it connects m2m_name to dedicated instance. """

    m2m_field = getattr(instance, m2m_name)
    m2m_field.clear()
    model = m2m_field.model

    for item_name in items:
        item, _ = model.objects.get_or_create(name=item_name, **kwargs)
        m2m_field.add(item.pk)


class empty:
    """" Class to substitude None value in dictionary key
    to make possible to have multiple None keys in the same dictionary. """
    pass


def update_fk_multiple(instance, field_name, field_values, field_key):
    """ Helper method that updates field_name for given instance. If instance does not have
    related object with field_key given in field_values or field_key in field_values is None,
    then new Foreign Key object is created and assigned to instance.
    Finally, all related objects that were not passed in field_values are deleted. """

    fk_field = instance._meta.get_field(field_name)
    model = fk_field.related_model

    queryset = getattr(instance, field_name).all()

    objects_mapping = {getattr(obj, field_key): obj for obj in queryset}
    data_mapping = {
        item[field_key] if item[field_key] is not None else empty: item
        for item in field_values
    }

    # Perform creations and updates.
    for key, data in data_mapping.items():
        obj = objects_mapping.pop(key, empty)
        data.pop('id', None)
        if obj == empty:
            data[fk_field.field.name] = instance
            model.objects.create(**data)
        else:
            obj.update(**data)

    # Perform deletions.
    for key, obj in objects_mapping.items():
        if key not in data_mapping:
            obj.delete()


def response_ok(detail):
    return {'detail': detail}
