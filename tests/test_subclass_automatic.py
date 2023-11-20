"""Test subclass handling."""

import pytest

from zninit import Descriptor, ZnInit


class Parent(ZnInit):
    """Parent class."""

    def __init__(self, **kwargs):
        """Define __init__."""
        self.name = kwargs.pop("name", None)
        if len(kwargs) > 0:
            raise TypeError(f"'{kwargs}' are an invalid keyword argument")


class Child(Parent):
    """Child class."""

    _init_subclass_basecls_ = Parent
    text = Descriptor()


class ChildOld(Parent):
    """Child class."""

    init_subclass_basecls = Parent
    text = Descriptor()


@pytest.mark.parametrize("cls", (Child, ChildOld))
def test_subclass_init(cls):
    """Test subclass init."""
    instance = cls(name="Test", text="Hello World")
    assert instance.name == "Test"
    assert instance.text == "Hello World"

    instance = Parent(name="Test")
    assert instance.name == "Test"

    with pytest.raises(TypeError):
        _ = cls(name="Test", text="Hello World", data="Lorem Ipsum")

    with pytest.raises(TypeError):
        _ = cls(name="Test")

    instance = cls(text="Hello World")
    assert instance.name is None
    assert instance.text == "Hello World"
