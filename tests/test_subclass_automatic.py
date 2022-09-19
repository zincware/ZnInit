import pytest

from zninit import Descriptor, ZnInit


class Parent(ZnInit):
    def __init__(self, **kwargs):
        self.name = kwargs.pop("name", None)
        if len(kwargs) > 0:
            raise TypeError(f"'{kwargs}' are an invalid keyword argument")


class Child(Parent):
    init_subclass_basecls = Parent
    text = Descriptor()


def test_subclass_init():
    instance = Child(name="Test", text="Hello World")
    assert instance.name == "Test"
    assert instance.text == "Hello World"

    instance = Parent(name="Test")
    assert instance.name == "Test"

    with pytest.raises(TypeError):
        _ = Child(name="Test", text="Hello World", data="Lorem Ipsum")

    with pytest.raises(TypeError):
        _ = Child(name="Test")

    instance = Child(text="Hello World")
    assert instance.name is None
    assert instance.text == "Hello World"
