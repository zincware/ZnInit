"""Definition and utils for the Descriptor class."""

from __future__ import annotations

import contextlib
import functools
import sys
import typing
import weakref

with contextlib.suppress(ImportError):
    import typeguard


class Empty:  # pylint: disable=too-few-public-methods
    """ZnInit Version of None to distinguish default version from None.

    When checking if something has a default we can not use 'value is None'
    because 'None' could be the default. Therefore, we use 'value is zninit.Empty'
    """


class Descriptor:  # pylint: disable=too-many-instance-attributes
    """Simple Python Descriptor that allows adding.

    This class allows to add metadata to arbitrary class arguments:

    References
    ----------
    https://docs.python.org/3/howto/descriptor.html

    Examples
    --------
    >>> from zninit.descriptor import Descriptor
    >>>
    >>> class MyDescriptor(Descriptor):
    >>>     metadata = "Custom Metadata"
    >>>
    >>> class SomeCls:
    >>>     value = MyDescriptor()
    >>>     def __init__(self, value):
    >>>         self.value = value
    >>>
    >>> print(SomeCls.value.metadata)
    >>> # "Custom Metadata"


    """

    def __init__(
        self,
        default=Empty,
        owner=None,
        instance=None,
        name="",
        use_repr: bool = True,
        repr_func: typing.Callable = repr,
        check_types: bool = False,
        metadata: dict = None,
        frozen: bool = False,
        on_setattr: typing.Callable = None,
    ):  # pylint: disable=too-many-arguments
        """Define a Descriptor object.

        Parameters
        ----------
        owner:
            overwrite Descriptor owner
        instance:
            overwrite Descriptor instance
        name: str
            overwrite Descriptor name
        default:
            Any default value to __get__ if the __set__ was never called.
        use_repr: bool, default=True
            This information is used by the ZnInit.__repr__ to check if this
            descriptor should be used in the __repr__ string.
        check_types: bool, default=False
            Check the type when using __set__ against the type annotation.
        frozen: bool, default=False
            Freeze the attribute after the first __set__ call.
        metadata: dict, default=None
            additional metadata for the descriptor.
        repr_func: Callable, default=repr
            A callable that will be used to compute the _repr_ of the descriptor.
        on_setattr: Callable, default=None
            A callable that is run whenever an attribute is set via 'class.myattr = value'
             or 'setattr(class, "mattr", value)'.
        """
        self._default = default
        self._owner = owner
        self._instance = instance
        self._name = name
        self.use_repr = use_repr
        self.check_types = check_types
        self.metadata = metadata or {}
        self.frozen = frozen
        self.get_repr = repr_func
        self.on_setattr = on_setattr
        self._frozen = weakref.WeakKeyDictionary()
        if check_types and ("typeguard" not in sys.modules):
            raise ImportError(
                "Need to install 'pip install zninit[typeguard]' for type checking."
            )

    @classmethod
    def get_dict(cls, instance: typing.Any) -> dict:
        """Get a {attribute-name: value} dict from instance for this descriptor."""
        descriptors = get_descriptors(cls, self=instance)
        return {
            descriptor.name: getattr(instance, descriptor.name)
            for descriptor in descriptors
        }

    @property
    def name(self):
        """Property for the name attribute to protect changing it."""
        return self._name

    @property
    def owner(self):
        """Property for the owner attribute to protect changing it."""
        return self._owner

    @property
    def instance(self):
        """Property for the instance attribute to protect changing it."""
        return self._instance

    @property
    def default(self):
        """Property for the default attribute to protect changing it."""
        return self._default

    @functools.cached_property
    def annotation(self):
        """Get the annotation from the owner.

        Raises
        ------
        KeyError:
            if type checking and the descriptor has no annotation.
        """
        try:
            annotations_ = self.owner.__annotations__
        except AttributeError:
            annotations_ = {}

        if self.check_types and self.name not in annotations_:
            raise KeyError(
                f"Could not find 'annotation' for {self.name} in '{self.owner}' with"
                " 'check_types=True'"
            )
        return annotations_.get(self.name)

    def __set_name__(self, owner, name):
        """Store name of the descriptor in the parent class."""
        self._owner = owner
        self._name = name

    def __get__(self, instance, owner=None):
        """Get from instance.__dict__.

        Raises
        ------
        AttributeError: if the value is not in the instance.__dict__ or in self.default
        """
        self._instance = instance
        if instance is None:
            return self
        value = instance.__dict__.get(self.name, self.default)
        if value is Empty:
            raise AttributeError(
                f"'{instance.__class__.__name__}.{self.name}' is not set"
            )
        return value

    def __set__(self, instance, value):
        """Save value to instance.__dict__."""
        if self._frozen.get(instance, False):
            raise TypeError(f"Frozen attribute '{self.name}' can not be changed.")
        if self.on_setattr is not None:
            value = self.on_setattr(value)
        if self.check_types:
            typeguard.check_type(
                argname=self.name, value=value, expected_type=self.annotation
            )
        self._instance = instance
        instance.__dict__[self.name] = value
        if self.frozen:
            self._frozen[instance] = True


DescriptorTypeT = typing.TypeVar("DescriptorTypeT", bound=Descriptor)


def check_descriptor_in_lst(descriptor, descriptor_lst: list) -> bool:
    """Return True if the descriptor appears in given list of descriptors."""
    for allowed_descriptor in descriptor_lst:
        if isinstance(descriptor, allowed_descriptor):
            return True
    return False


def get_descriptors(
    descriptor=Descriptor, *, self=None, cls=None
) -> typing.List[DescriptorTypeT]:
    """Get a list of all descriptors inheriting from "descriptor".

    Parameters
    ----------
    cls:
        any python class
    self:
        any python class instance
    descriptor:
        any object inheriting from descriptor

    Returns
    -------
    list
        a list of the found descriptor objects

    """
    if self is None and cls is None:
        raise ValueError("Either self or cls must not be None")
    if self is not None and cls is not None:
        raise ValueError("Either self or cls must be None")
    if self is not None:
        cls = type(self)
    if not isinstance(descriptor, (list, tuple)):
        descriptor = (descriptor,)
    lst = []
    try:
        for option in dir(cls):
            value = getattr(cls, option)
            if check_descriptor_in_lst(value, descriptor):
                lst.append(value)
    except AttributeError as err:
        raise AttributeError(
            "Trying to call 'Descriptor.__get__(instance=None)' to retrieve the"
            " Descriptor instance. Make sure you implemented that case in the __get__"
            " method."
        ) from err
    return lst
