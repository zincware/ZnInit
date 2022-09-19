import pytest

from zninit import Descriptor, ZnInit

# autocomplete issue https://youtrack.jetbrains.com/issue/PY-38072


class Params(Descriptor):
    pass


class Outs(Descriptor):
    pass


class SingleClsDefaults(ZnInit):
    param1 = Descriptor()
    param2 = Descriptor("World")


class ParentClsPlain(ZnInit):
    """A parent class without any changes"""


class ChildPlainCls(ParentClsPlain):
    parameter: int = Params()


class ChildPlainClsInit(ParentClsPlain):
    def __init__(self, parameter):
        super().__init__()
        self.parameter = parameter


class ParentCls(ZnInit):
    parameter: int = Params()


class DefaultIsNone(ZnInit):
    parameter: int = Descriptor(None)


class ChildCls(ParentCls):
    pass


class OnlyParamsInInit(ZnInit):
    init_descriptors = [Params]

    parameter: int = Params()
    output = Outs()


class ChildClsInit(ParentCls):
    def __init__(self, parameter, value):
        super().__init__(
            parameter=parameter
        )  # super(ChildClsInit, self).__init__ does not work!
        self.value = value


def test_ParentClsPlain():
    _ = ParentClsPlain()
    with pytest.raises(TypeError):
        _ = ParentClsPlain(paramter=10)


def test_ChildPlainCls():
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

    child = ChildPlainCls(parameter=10)
    assert child.parameter == 10


def test_ChildPlainClsInit():
    x = ChildPlainClsInit(parameter=10)
    assert x.parameter == 10


def test_ParentCls():
    with pytest.raises(TypeError) as err:
        _ = ParentCls()

    assert (
        err.value.args[0]
        == "ParentCls.__init__() missing 1 required keyword-only argument: 'parameter'"
    )

    parent = ParentCls(parameter=10)
    assert parent.parameter == 10


def test_ChildCls():
    with pytest.raises(TypeError) as err:
        _ = ChildCls()

    assert (
        err.value.args[0]
        == "ChildCls.__init__() missing 1 required keyword-only argument: 'parameter'"
    )

    child = ChildCls(parameter=10)
    assert child.parameter == 10


def test_ChildClsInit():
    child = ChildClsInit(parameter=10, value=5)
    assert child.parameter == 10
    assert child.value == 5


def test_SingleClsDefaults():
    instance = SingleClsDefaults(param1="Hello")
    assert instance.param1 + " " + instance.param2 == "Hello World"

    instance = SingleClsDefaults(param1="Lorem", param2="Ipsum")
    assert instance.param1 + " " + instance.param2 == "Lorem Ipsum"


def test_DefaultIsNone():
    instance = DefaultIsNone()
    assert instance.parameter is None
    instance = DefaultIsNone(parameter=42)
    assert instance.parameter == 42


def test_OnlyParamsInInit():
    instance = OnlyParamsInInit(parameter=10)
    assert instance.parameter == 10
    with pytest.raises(AttributeError):
        _ = instance.output
