"""Test for the automatic __init__."""
import pytest

from zninit import Descriptor, ZnInit

# autocomplete issue https://youtrack.jetbrains.com/issue/PY-38072


class Params(Descriptor):
    """Descriptor child."""

    pass


class Outs(Descriptor):
    """Descriptor child."""

    pass


class SingleClsDefaults(ZnInit):
    """ZnInit child."""

    param1 = Descriptor()
    param2 = Descriptor("World")


class ParentClsPlain(ZnInit):
    """A parent class without any changes."""


class ChildPlainCls(ParentClsPlain):
    """ZnInit child."""

    parameter: int = Params()


class ChildPlainClsInit(ParentClsPlain):
    """ZnInit child."""

    def __init__(self, parameter):
        """Define __init__."""
        super().__init__()
        self.parameter = parameter


class ParentCls(ZnInit):
    """ZnInit child."""

    parameter: int = Params()


class DefaultIsNone(ZnInit):
    """ZnInit child."""

    parameter: int = Descriptor(None)


class ChildCls(ParentCls):
    """ZnInit child."""

    pass


class OnlyParamsInInit(ZnInit):
    """ZnInit child."""

    _init_descriptors_ = [Params]

    parameter: int = Params()
    output = Outs()


class OnlyParamsInInitOld(ZnInit):
    """ZnInit child."""

    init_descriptors = [Params]

    parameter: int = Params()
    output = Outs()


class ChildClsInit(ParentCls):
    """ZnInit child."""

    def __init__(self, parameter, value):
        """Define __init__."""
        super().__init__(
            parameter=parameter
        )  # super(ChildClsInit, self).__init__ does not work!
        self.value = value


def test_ParentClsPlain():
    """ZnInit Test."""
    _ = ParentClsPlain()
    with pytest.raises(TypeError):
        _ = ParentClsPlain(paramter=10)


def test_ChildPlainCls():
    """ZnInit Test."""
    with pytest.raises(TypeError) as err:
        _ = ChildPlainCls()

    assert (
        err.value.args[0]
        == "ChildPlainCls.__init__() missing 1 required keyword-only argument:"
        " 'parameter'"
    )

    with pytest.raises(TypeError) as err:
        _ = ChildPlainCls(10)

    assert (
        err.value.args[0]
        == "ChildPlainCls.__init__() takes 1 positional argument but 2 were given"
    )

    with pytest.raises(TypeError) as err:
        _ = ChildPlainCls(q=10)

    assert err.value.args[0].endswith("__init__() got an unexpected keyword argument 'q'")

    with pytest.raises(TypeError) as err:
        _ = ChildPlainCls(parameter=10, q=10)

    assert err.value.args[0].endswith("__init__() got an unexpected keyword argument 'q'")

    child = ChildPlainCls(parameter=10)
    assert child.parameter == 10


def test_ChildPlainClsInit():
    """ZnInit Test."""
    x = ChildPlainClsInit(parameter=10)
    assert x.parameter == 10


def test_ParentCls():
    """ZnInit Test."""
    with pytest.raises(TypeError) as err:
        _ = ParentCls()

    assert (
        err.value.args[0]
        == "ParentCls.__init__() missing 1 required keyword-only argument: 'parameter'"
    )

    parent = ParentCls(parameter=10)
    assert parent.parameter == 10


def test_ChildCls():
    """ZnInit Test."""
    with pytest.raises(TypeError) as err:
        _ = ChildCls()

    assert (
        err.value.args[0]
        == "ChildCls.__init__() missing 1 required keyword-only argument: 'parameter'"
    )

    child = ChildCls(parameter=10)
    assert child.parameter == 10


def test_ChildClsInit():
    """ZnInit Test."""
    child = ChildClsInit(parameter=10, value=5)
    assert child.parameter == 10
    assert child.value == 5


def test_SingleClsDefaults():
    """ZnInit Test."""
    instance = SingleClsDefaults(param1="Hello")
    assert instance.param1 + " " + instance.param2 == "Hello World"

    instance = SingleClsDefaults(param1="Lorem", param2="Ipsum")
    assert instance.param1 + " " + instance.param2 == "Lorem Ipsum"


def test_DefaultIsNone():
    """ZnInit Test."""
    instance = DefaultIsNone()
    assert instance.parameter is None
    instance = DefaultIsNone(parameter=42)
    assert instance.parameter == 42


@pytest.mark.parametrize("cls", (OnlyParamsInInit, OnlyParamsInInitOld))
def test_OnlyParamsInInit(cls):
    """ZnInit Test."""
    instance = cls(parameter=10)
    assert instance.parameter == 10
    with pytest.raises(AttributeError):
        _ = instance.output

    with pytest.raises(TypeError):
        cls(parameter=10, output=25)
