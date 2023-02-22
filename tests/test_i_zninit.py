"""General 'ZnInit' integration tests."""
import pytest

import zninit


class GetItemMeta(type):
    """Metaclass for general testing."""

    def __getitem__(cls, item):
        """General purpose metaclass."""
        return item


class ExampleCls(zninit.ZnInit, metaclass=GetItemMeta):
    """Example 'ZnInit' with metaclass."""

    parameter = zninit.Descriptor()
    frozen_parameter = zninit.Descriptor(None, frozen=True)


def test_ExampleCls():
    """Test 'ZnInit' with a metaclass."""
    example = ExampleCls(parameter=25)
    assert example.parameter == 25
    assert ExampleCls[42] == 42
    assert zninit.Descriptor.get_dict(example) == {
        "parameter": 25,
        "frozen_parameter": None,
    }


def test_frozen_parameter():
    """Test frozen parameter."""
    example = ExampleCls(parameter=18, frozen_parameter=42)
    assert example.frozen_parameter == 42
    with pytest.raises(TypeError):
        example.frozen_parameter = 43

    example = ExampleCls(parameter=18, frozen_parameter=42)
    assert example.frozen_parameter == 42
    with pytest.raises(TypeError):
        example.frozen_parameter = 43


def test_frozen_parameter_default():
    """Test frozen_parameter with default value."""
    example = ExampleCls(parameter=18)
    assert example.frozen_parameter is None
    with pytest.raises(TypeError):
        example.frozen_parameter = 43

    example = ExampleCls(parameter=18, frozen_parameter=42)
    assert example.frozen_parameter == 42
    with pytest.raises(TypeError):
        example.frozen_parameter = 43
