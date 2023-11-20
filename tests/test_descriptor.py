"""Test ZnInit descriptors."""

import pytest

from zninit import Descriptor, get_descriptors


class ExampleCls:
    """Example class."""

    desc = Descriptor()


class ExampleChild(ExampleCls):
    """Example Child."""

    pass


def test_get_descriptor():
    """ZnInit test."""
    assert isinstance(ExampleCls.desc, Descriptor)


def test_descriptor_name():
    """ZnInit test."""
    descriptor = ExampleCls.desc
    assert descriptor.name == "desc"


def test_descriptor_owner():
    """ZnInit test."""
    descriptor = ExampleCls.desc
    assert descriptor.owner == ExampleCls


@pytest.mark.parametrize("access", ("get", "set"))
def test_get_instance(access):
    """ZnInit test."""
    desc = ExampleCls.desc

    cls = ExampleCls()
    if access == "set":
        cls.desc = 25
    elif access == "get":
        with pytest.raises(AttributeError):
            _ = cls.desc

    assert desc.instance == cls


def test_descriptor_set():
    """ZnInit test."""
    desc = ExampleCls.desc
    cls = ExampleCls()
    cls.desc = 42
    assert cls.__dict__[desc.name] == 42


def test_descriptor_get():
    """ZnInit test."""
    desc = ExampleCls.desc
    cls = ExampleCls()
    cls.__dict__[desc.name] = 42
    assert cls.desc == 42


@pytest.mark.parametrize("cls", (ExampleCls, ExampleChild))
def test_get_descriptors_cls(cls):
    """ZnInit test."""
    instance = cls
    assert get_descriptors(Descriptor, cls=instance) == [cls.desc]


@pytest.mark.parametrize("cls", (ExampleCls, ExampleChild))
def test_get_descriptors_self(cls):
    """ZnInit test."""
    self = cls()
    assert get_descriptors(Descriptor, self=self) == [cls.desc]


def test_get_descriptors_exceptions():
    """ZnInit test."""
    with pytest.raises(ValueError):
        get_descriptors(Descriptor)

    with pytest.raises(ValueError):
        get_descriptors()

    with pytest.raises(ValueError):
        get_descriptors(Descriptor, self=ExampleCls(), cls=ExampleCls)


class CustomDescriptor1(Descriptor):
    """ZnInit descriptor."""

    pass


class CustomDescriptor2(Descriptor):
    """ZnInit descriptor."""

    pass


class MultipleDescriptors:
    """ZnInit Descriptor container."""

    desc1_1 = CustomDescriptor1()
    desc1_2 = CustomDescriptor1()

    desc2_1 = CustomDescriptor2()
    desc2_2 = CustomDescriptor2()


def test_get_custom_descriptors():
    """ZnInit test."""
    cls = MultipleDescriptors
    assert get_descriptors(Descriptor, cls=cls) == [
        cls.desc1_1,
        cls.desc1_2,
        cls.desc2_1,
        cls.desc2_2,
    ]
    assert get_descriptors(CustomDescriptor1, cls=cls) == [cls.desc1_1, cls.desc1_2]
    assert get_descriptors(CustomDescriptor2, cls=cls) == [cls.desc2_1, cls.desc2_2]

    self = MultipleDescriptors()
    assert get_descriptors(Descriptor, self=self) == [
        cls.desc1_1,
        cls.desc1_2,
        cls.desc2_1,
        cls.desc2_2,
    ]
    assert get_descriptors(CustomDescriptor1, self=self) == [cls.desc1_1, cls.desc1_2]
    assert get_descriptors(CustomDescriptor2, self=self) == [cls.desc2_1, cls.desc2_2]


def test_get_dict_custom_descriptors():
    """Test the get_dict method from descriptors."""
    instance = MultipleDescriptors()
    instance.desc1_1 = "1_1"
    instance.desc1_2 = "1_2"
    instance.desc2_1 = "2_1"
    instance.desc2_2 = "2_2"

    assert CustomDescriptor1.get_dict(instance) == {"desc1_1": "1_1", "desc1_2": "1_2"}
    assert CustomDescriptor2.get_dict(instance) == {"desc2_1": "2_1", "desc2_2": "2_2"}
    assert Descriptor.get_dict(instance) == {
        "desc1_1": "1_1",
        "desc1_2": "1_2",
        "desc2_1": "2_1",
        "desc2_2": "2_2",
    }


def test_get_desc_values():
    """ZnInit test."""
    self = MultipleDescriptors()

    self.desc1_1 = "Hello"
    self.desc1_2 = "World"

    desc1_1, desc1_2 = get_descriptors(CustomDescriptor1, self=self)

    assert desc1_1.__get__(self) == "Hello"
    assert desc1_2.__get__(self) == "World"


class FrozenExample:
    """ZnInit Frozen Descriptor."""

    value = Descriptor(frozen=True)


def test_frozen_descriptor():
    """Test a frozen descriptor."""
    example = FrozenExample()
    example.value = 42
    with pytest.raises(TypeError):
        example.value = 25
    assert example.value == 42

    # Running twice is a test.
    example = FrozenExample()
    example.value = 42
    with pytest.raises(TypeError):
        example.value = 25
    assert example.value == 42


class WithMetadata:
    """ZnInit Descriptor with metadata."""

    value = Descriptor(metadata={"foo": "bar"})


def test_descriptor_metadata():
    """Test a descriptor with metadata."""
    assert WithMetadata.value.metadata["foo"] == "bar"


class WithSetAttr:
    """Modify the value before saving it."""

    value = Descriptor(on_setattr=lambda value: value + 1)
    value_frozen = Descriptor(frozen=True, on_setattr=lambda value: value + 1)


def test_with_setattr():
    """Test a descriptor with on_setattr."""
    example = WithSetAttr()
    example.value = 1
    assert example.value == 2

    example.value_frozen = 1
    assert example.value_frozen == 2

    with pytest.raises(TypeError):
        example.value_frozen = 10
