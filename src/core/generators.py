import os
import faker
import random

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

fake = faker.Faker()
DEFAULT_USER_PASSWORD = 'admin123@'
DEFAULT_ADMIN_EMAIL = 'admin@example.com'


class FileFaker:
    media_file_counters = {}

    def __init__(self, base_dir=None, use_loop=True):
        self.use_loop = use_loop
        self.base_dir = base_dir or settings.STATICFILES_DIRS[0]

    def image(self, from_folder):
        path = self.get_path(from_folder)
        filenames = self.get_filenames(path)
        filename = self.select_filename(filenames, path)
        return self.to_simple_uploaded_file(path, filename)

    def get_path(self, folder):
        return os.path.join(self.base_dir, folder)

    def get_filenames(self, path):
        extensions = ('.jpeg', '.jpg', '.png')
        filenames = (f for f in os.listdir(path))
        return [f for f in filenames if any([f.endswith(e) for e in extensions])]

    def select_filename(self, filenames, path):
        if self.use_loop:
            self.media_file_counters.setdefault(path, 0)
            idx = self.media_file_counters[path]
            self.media_file_counters[path] += 1
            return filenames[idx % len(filenames)]
        else:
            return random.choice(filenames)

    def to_simple_uploaded_file(self, path, filename):
        full_path = os.path.join(path, filename)
        file = open(full_path, 'rb')
        return SimpleUploadedFile(name=filename, content=file.read(), content_type='image/jpg')


fake_file = FileFaker()


class Lazy:
    """ Class to delay evaluating a generation of object related instances
    to prevent overloading database with unused records. """

    def __init__(self, func, kwargs=None):
        kwargs = kwargs or {}
        self.func = func

        func_name = self.func.__name__
        if func_name.startswith('generate_'):
            model_name = func_name[9:]
            kwargs = kwargs.get(model_name, {})

        self.kwargs = kwargs

    def __call__(self):
        return self.func(**self.kwargs)


class Random:
    def __init__(self, choices):
        self.choices = choices

    def __call__(self):
        return random.choice(self.choices)


def override_defaults(default_attrs, overrides):
    """ Function to override default passed attributes and evaluate lazy generation of
    all related instances. """

    attrs = {}
    for key in default_attrs.keys():
        attr = overrides.get(key, default_attrs[key])
        if isinstance(attr, (Lazy, Random)):
            attr = attr()
        attrs[key] = attr
    return attrs


def populatable(func):
    """ Decorator that adds `population` parameter that can be passed to generator
    to call it multiple times.
    :returns a list of objects if population is specified or single object otherwise. """

    def decorator(**kwargs):
        population = kwargs.pop('population', None)
        if population is None:
            return func(**kwargs)
        return [func(**kwargs) for __ in range(population)]

    return decorator


def random_enum(enum):
    return random.choice([v for k, v in enum])
