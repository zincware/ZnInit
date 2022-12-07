"""General 'ZnInit' integration tests."""
import zninit


class GetItemMeta(type):
    """Metaclass for general testing."""

    def __getitem__(cls, item):
        """General purpose metaclass."""
        return item


class ExampleCls(zninit.ZnInit, metaclass=GetItemMeta):
    """Example 'ZnInit' with metaclass."""

    parameter = zninit.Descriptor()


def test_ExampleCls():
    """Test 'ZnInit' with a metaclass."""
    example = ExampleCls(parameter=25)
    assert example.parameter == 25
    assert ExampleCls[42] == 42
