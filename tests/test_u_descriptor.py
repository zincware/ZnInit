"""Unit tests for 'ZnInit'."""
import collections.abc
import sys
import typing

import pytest

from zninit import Descriptor, get_descriptors


class CustomDescriptor(Descriptor):
    """Custom Descriptor."""

    def __get__(self, instance, owner=None):
        """Get from instance.__dict__."""
        self._instance = instance
        # Test the following part missing
        # if instance is None:
        #     return self
        return instance.__dict__.get(self.name, self.default)


class ExampleClass:
    """Example class with custom descriptor."""

    param1 = CustomDescriptor()


def test_get_descriptor_err():
    """Zninit test."""
    with pytest.raises(AttributeError) as err:
        _ = get_descriptors(cls=ExampleClass)
    assert err.value.args[0].startswith(
        "Trying to call 'Descriptor.__get__(instance=None)' to retrieve the Descriptor"
        " instance"
    )

    # now with self

    with pytest.raises(AttributeError) as err:
        _ = get_descriptors(self=ExampleClass())
    assert err.value.args[0].startswith(
        "Trying to call 'Descriptor.__get__(instance=None)' to retrieve the Descriptor"
        " instance"
    )


def test_check_type_no_annotation():
    """Check for empty annotations."""

    class ClsWithoutAnnotations:
        empty = Descriptor(check_types=True)

    instance = ClsWithoutAnnotations()

    with pytest.raises(KeyError):
        ClsWithoutAnnotations.empty.annotation

    with pytest.raises(KeyError):
        instance.empty = "Not empty"


def test_check_type():
    """Test check_type."""

    class ClsWithAnnotations:
        empty: bool = Descriptor(check_types=True)
        iterable: collections.abc.Iterable = Descriptor(check_types=True)
        list_bool: typing.List[bool] = Descriptor(check_types=True)
        number: typing.Union[int, float] = Descriptor(check_types=True)

    instance = ClsWithAnnotations()

    _ = instance.empty = True
    with pytest.raises(TypeError):
        _ = instance.empty = "True"

    _ = instance.iterable = list(range(5))
    _ = instance.iterable = (x for x in range(5))
    _ = instance.iterable = set(range(5))

    with pytest.raises(TypeError):
        _ = instance.iterable = True

    _ = instance.list_bool = [True, False]

    with pytest.raises(TypeError):
        _ = instance.list_bool = True

    _ = instance.number = 5
    _ = instance.number = 5.0

    with pytest.raises(TypeError):
        _ = instance.number = "5.0"

    assert ClsWithAnnotations.empty.annotation == bool
    assert ClsWithAnnotations.iterable.annotation == collections.abc.Iterable
    assert ClsWithAnnotations.list_bool.annotation == typing.List[bool]
    assert ClsWithAnnotations.number.annotation == typing.Union[int, float]


def test_no_typeguard():
    """Check what happens when typeguard is not available."""
    sys.modules.pop("typeguard")
    with pytest.raises(ImportError):
        _ = Descriptor(check_types=True)
    import typeguard  # noqa=F401

    _ = Descriptor(check_types=True)
