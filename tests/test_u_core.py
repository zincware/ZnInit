"""'ZnInit' unit tests."""
from zninit import Descriptor, ZnInit
from zninit.core import get_args_type_error, get_init_type_error


class ClsDefaultMixed(ZnInit):
    """Class with default / none default values."""

    init_descriptors = [Descriptor]

    param1 = Descriptor()
    param2 = Descriptor("World")


class DoNotUseRepr(ZnInit):
    """Class with disabled repr."""

    init_descriptors = [Descriptor]
    param1 = Descriptor(use_repr=False)
    param2 = Descriptor(use_repr=True)


def test_get_auto_init_kwargs():
    """Test auto init kwargs."""
    kwargs_no_default, kwargs_with_default = ClsDefaultMixed._get_auto_init_kwargs()
    assert kwargs_no_default == ["param1"]
    assert kwargs_with_default == {"param2": "World"}


def test_get_args_type_error():
    """Test the args TypeError."""
    err = get_args_type_error(args=["a", "b"], cls_name="ABC", uses_auto_init=True)
    assert err.args[0] == "ABC.__init__() takes 1 positional argument but 3 were given"

    err = get_args_type_error(args=["a", "b"], cls_name="ABC", uses_auto_init=False)
    assert (
        err.args[0]
        == "super(ABC, self).__init__() takes 1 positional argument but 3 were given"
    )


def test_get_init_type_error():
    """Test init TypeError."""
    err = get_init_type_error(required_keys=["a"], cls_name="ABC", uses_auto_init=True)
    assert err.args[0] == "ABC.__init__() missing 1 required keyword-only argument: 'a'"

    err = get_init_type_error(required_keys=["a"], cls_name="ABC", uses_auto_init=False)
    assert (
        err.args[0]
        == "super(ABC, self).__init__() missing 1 required keyword-only argument: 'a'"
    )

    err = get_init_type_error(
        required_keys=["a", "b"], cls_name="ABC", uses_auto_init=True
    )
    assert (
        err.args[0]
        == "ABC.__init__() missing 2 required keyword-only arguments: 'a' and 'b'"
    )

    err = get_init_type_error(
        required_keys=["a", "b"], cls_name="ABC", uses_auto_init=False
    )
    assert (
        err.args[0]
        == "super(ABC, self).__init__() missing 2 required keyword-only arguments: 'a'"
        " and 'b'"
    )

    err = get_init_type_error(
        required_keys=["a", "b", "c"], cls_name="ABC", uses_auto_init=True
    )
    assert (
        err.args[0]
        == "ABC.__init__() missing 3 required keyword-only arguments: 'a', 'b' and 'c'"
    )

    err = get_init_type_error(
        required_keys=["a", "b", "c"], cls_name="ABC", uses_auto_init=False
    )
    assert (
        err.args[0]
        == "super(ABC, self).__init__() missing 3 required keyword-only arguments: 'a',"
        " 'b' and 'c'"
    )


def test_repr():
    """Test the __repr__."""
    instance = ClsDefaultMixed(param1="Hello")
    assert repr(instance) == "ClsDefaultMixed(param1='Hello', param2='World')"

    instance = DoNotUseRepr(param1="Hello", param2="World")
    assert repr(instance) == "DoNotUseRepr(param2='World')"

    DoNotUseRepr.use_repr = False
    assert repr(DoNotUseRepr(param1="Hello", param2="World")).startswith(
        "<test_u_core.DoNotUseRepr object at"
    )
