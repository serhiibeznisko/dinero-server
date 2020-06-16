from enum import Enum, EnumMeta, unique

from django.utils.translation import ugettext_lazy as _


class ChoicesEnumMeta(EnumMeta):
    """ A metaclass which allows to iterate over enum class. """

    def __iter__(self):
        return ((choice.name, choice.value) for choice in super().__iter__())


@unique
class ChoicesEnum(str, Enum, metaclass=ChoicesEnumMeta):
    def __str__(self):
        return self.name

    def __eq__(self, other):
        """ This allows to compare strings with enum name to the actual enum without referencing to enum.name. """
        return str(self) == str(other)

    def __hash__(self):
        """ Allows to i.a. use enum as a dictionary key. """
        return hash(self.name)

    def __gt__(self, other):
        """ Enum is greater if it is declared below other enum. """
        return self.index(str(self)) > self.index(str(other))

    def __ge__(self, other):
        """ It just has to be defined explicitly. """
        return self > other or self == other

    def __lt__(self, other):
        """ Enum is lesser if it is declared above other enum. """
        return self.index(str(self)) < self.index(str(other))

    def __le__(self, other):
        """ It just has to be defined explicitly. """
        return self < other or self == other

    @classmethod
    def index(cls, enum_name: str) -> int:
        """ Return index of enum relative to the order declared in the class, counting from 1. """
        return [name for name, value in cls].index(enum_name) + 1

    @classmethod
    def values(cls):
        return [value for name, value in cls]

    @classmethod
    def names(cls):
        return [name for name, value in cls]

    @classmethod
    def contains(cls, enum_name: str) -> bool:
        return any(enum_name == value for name, value in cls)


class TransactionStatus(ChoicesEnum):
    PENDING = 'PENDING'
    SUCCESSFUL = 'SUCCESSFUL'
    CANCELED = 'CANCELED'
