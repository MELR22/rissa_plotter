from abc import ABC, abstractmethod


class Validator(ABC):
    def __set_name__(self, owner, name):
        self.private_name = "_" + name

    def __get__(self, obj, objtype=None):
        return getattr(obj, self.private_name)

    def __set__(self, obj, value):
        self.validate(value)
        setattr(obj, self.private_name, value)

    @abstractmethod
    def validate(self):
        pass


class ValidNumber(Validator):
    """
    Validate if a number is between a minimum and maximum value.

    Parameters
    ----------
    min_value : int | float
        Minimum value of the number.
    max_value : int | float
        Maximum value of the number.
    """

    def __init__(self, min_value, max_value):
        self.min_value = min_value
        self.max_value = max_value

    def validate(self, value):
        if value is None:
            return  # Allow None
        if not (self.min_value <= value <= self.max_value):
            raise ValueError(
                f"{value} is not between {self.min_value} and {self.max_value}"
            )


class ValidMethod(Validator):
    """
    Validate if a method is a valid as input.

    Parameters
    ----------
    valid_methods
        Specify valid methods.
    """

    def __init__(self, *valid_methods):
        self.valid_methods = set(valid_methods)

    def validate(self, value):
        if value not in self.valid_methods:
            raise ValueError(
                f"{value} is not a valid method. Valid methods are: {self.valid_methods}"
            )
