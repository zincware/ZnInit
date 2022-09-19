import pytest

from zninit import Descriptor, get_descriptors


class CustomDescriptor(Descriptor):
    def __get__(self, instance, owner=None):
        """Get from instance.__dict__"""
        self._instance = instance
        # Test the following part missing
        # if instance is None:
        #     return self
        return instance.__dict__.get(self.name, self.default)


class ExampleClass:
    param1 = CustomDescriptor()


def test_get_descriptor_err():
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
