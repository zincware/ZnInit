"""Functionality to generate the automatic __init__"""
from __future__ import annotations

import logging
import typing
from copy import deepcopy
from inspect import Parameter, Signature

from zninit.descriptor import Descriptor, Empty, get_descriptors

log = logging.getLogger(__name__)


# TODO write more tests for inheritance and TypeError(super.__)
# TODO write tests for positional only arguments


def get_args_type_error(args: list, cls_name: str, uses_auto_init: bool) -> TypeError:
    """Get a TypeError of args are used instead of kwargs"""
    if uses_auto_init:
        return TypeError(
            f"{cls_name}.__init__() takes 1 positional argument but {len(args) + 1} were"
            " given"
        )
    return TypeError(
        f"super({cls_name}, self).__init__() takes 1 positional argument but"
        f" {len(args) + 1} were given"
    )


def get_init_type_error(
    required_keys: list, cls_name: str, uses_auto_init: bool
) -> TypeError:
    """Get a TypeError similar to a wrong __init__"""
    if len(required_keys) == 1:
        if uses_auto_init:
            return TypeError(
                f"{cls_name}.__init__() missing 1 required keyword-only argument:"
                f" '{required_keys[0]}'"
            )
        return TypeError(
            f"super({cls_name}, self).__init__() missing 1 required keyword-only"
            f" argument: '{required_keys[0]}'"
        )

    if uses_auto_init:
        return TypeError(
            f"{cls_name}.__init__() missing {len(required_keys)} required"
            " keyword-only"
            " arguments:"
            f""" '{"', '".join(required_keys[:-1])}' and '{required_keys[-1]}'"""
        )
    return TypeError(
        f"super({cls_name}, self).__init__() missing"
        f" {len(required_keys)} required keyword-only"
        " arguments:"
        f""" '{"', '".join(required_keys[:-1])}' and '{required_keys[-1]}'"""
    )


def get_auto_init(
    kwargs_no_default: typing.List[str],
    kwargs_with_default: dict,
    super_init: typing.Callable,
):
    """Automatically create an __init__ based on fields

    Parameters
    ----------
    kwargs_no_default: list[str]
        A list that strings (required kwarg without default value) that will be used in
        the __init__, e.g. for [foo, bar] will create  __init__(self, foo, bar)
    kwargs_with_default: dict[str, any]
        A dict that contains the name of the kwarg as key and the default value
         (kwargs with default value) that will be used in
        the __init__, e.g. for {foo: None, bar: 10} will create
         __init__(self, foo=None, bar=10)
    super_init: Callable
        typically this is Node.__init__
    """

    kwargs_no_default = [] if kwargs_no_default is None else kwargs_no_default
    kwargs_with_default = {} if kwargs_with_default is None else kwargs_with_default

    def auto_init(self, *args, **kwargs):
        """Wrapper for the __init__"""
        # TODO accept args and raise custom error
        init_kwargs = {}
        required_keys = []
        uses_auto_init = getattr(self.__init__, "uses_auto_init", False)
        cls_name = self.__class__.__name__
        if len(args) > 0:
            raise get_args_type_error(args, cls_name, uses_auto_init)
        log.debug(f"The '__init__' uses auto_init: {uses_auto_init}")
        for kwarg_name in kwargs_no_default:
            try:  # pylint: disable=loop-try-except-usage
                init_kwargs[kwarg_name] = kwargs.pop(kwarg_name)
            except KeyError:
                required_keys.append(kwarg_name)

        if len(required_keys) > 0:
            raise get_init_type_error(required_keys, cls_name, uses_auto_init)

        init_kwargs.update(
            {name: kwargs.pop(name, value) for name, value in kwargs_with_default.items()}
        )

        super_init(self, **kwargs)  # call the super_init explicitly instead of super
        # must call the super_init first e.g. it is required to set the node_name
        for key, value in init_kwargs.items():
            setattr(self, key, value)

        try:
            self.post_init()
        except AttributeError:
            pass

    # we add this attribute to the __init__ to make it identifiable
    auto_init.uses_auto_init = True

    return auto_init


class ZnInit:
    """Parent class for automatic __init__ generation based on descriptrs

    Attributes
    -----------
    init_descriptors: list
        A list of the descriptor classes to be added to the init.
        This also supports subclasses of Descriptor.
    use_repr: bool
        Generate an automatic, dataclass like representation string.
    """

    init_descriptors: typing.List[Descriptor] = [Descriptor]
    use_repr: bool = True

    def __init_subclass__(cls, basecls=None, **kwargs):
        super().__init_subclass__(**kwargs)
        if basecls is None:
            basecls = ZnInit
        for inherited in cls.__mro__:
            # Go through the mro until you find the Node class.
            # If found an init before that class it will implement super
            # if not add the fields to the __init__ automatically.
            if inherited == basecls:
                break
            if inherited.__dict__.get("__init__") is not None:
                if not getattr(inherited.__init__, "uses_auto_init", False):
                    return cls

        log.debug(f"Found {basecls} instance - adding dataclass-like __init__")
        return cls._update_init(super_init=basecls.__init__)

    @classmethod
    def _get_descriptors(cls):
        return get_descriptors(descriptor=cls.init_descriptors, cls=cls)

    @classmethod
    def _update_init(cls, super_init):
        """Set the automatic __init__

        Parameters
        ----------
        cls: the cls to be updated
        super_init: run a super call if required

        Returns
        -------
        the updated cls instance

        """
        kwargs_no_default, kwargs_with_default = cls._get_auto_init_kwargs()
        signature_params = cls._get_auto_init_signature()

        # Add new __init__ to the subclass
        setattr(
            cls,
            "__init__",
            get_auto_init(kwargs_no_default, kwargs_with_default, super_init=super_init),
        )

        # Add new __signature__ to the subclass
        signature = Signature(parameters=signature_params)
        setattr(cls, "__signature__", signature)

        return cls

    @classmethod
    def _get_auto_init_kwargs(cls) -> (list, dict):
        """Get the keywords for the __init__

        Collect keywords with and without default values for the init

        Returns
        -------

        """
        kwargs_no_default = []
        kwargs_with_default = {}

        for descriptor in cls._get_descriptors():
            # For the new __init__
            if descriptor.default is Empty:
                kwargs_no_default.append(descriptor.name)
            else:
                kwargs_with_default[descriptor.name] = deepcopy(descriptor.default)

        return kwargs_no_default, kwargs_with_default

    @classmethod
    def _get_auto_init_signature(cls) -> (list, dict, list):
        """Iterate over ZnTrackOptions in the __dict__ and save the option name
        and create a signature Parameter

        Returns:
            kwargs_no_default: list
                a list of names that will be converted to kwargs
            kwargs_with_default: dict
                a dict of {name: default} that will be converted to kwargs
            signature_params: inspect.Parameter
        """
        signature_params = []
        cls_annotations = cls.__annotations__  # pylint: disable=no-member
        # fix for https://bugs.python.org/issue46930
        for descriptor in cls._get_descriptors():
            # For the new __signature__
            signature_params.append(
                Parameter(
                    # default=...
                    name=descriptor.name,
                    kind=Parameter.POSITIONAL_OR_KEYWORD,
                    annotation=cls_annotations.get(descriptor.name),
                )
            )
        return signature_params

    def __repr__(self):
        """Get a dataclass like representation of the ZnInit class"""
        if not self.use_repr:
            return super().__repr__()
        repr_str = f"{self.__class__.__name__}("
        fields = []
        for descriptor in self._get_descriptors():
            if not descriptor.use_repr:
                continue
            fields.append(f"{descriptor.name}={repr(getattr(self, descriptor.name))}")
        repr_str += ", ".join(fields)
        repr_str += ")"
        return repr_str

    def post_init(self):
        """Implement if cmds after the automatically generated __init__ should be run

        This only works if no __init__ is defined and the automatically generated
        __init__ from ZnTrack is used.
        """
        raise AttributeError(f"'{self}' object has no attribute 'post_init'")
