"""Provide a typed factory function for descriptors."""

from typing import Callable, Optional

from zninit.descriptor import Descriptor, Empty


def desc(
    default=Empty,
    owner=None,
    instance=None,
    name="",
    use_repr: bool = True,
    repr_func: Callable = repr,
    check_types: bool = False,
    metadata: Optional[dict] = None,
    frozen: bool = False,
    on_setattr: Optional[Callable] = None,
):
    """Create a Descriptor object.

    Forwards all arguments to the Descriptor.__init__ method.
    The return type is annotated as the type of the managed attribute
    to enable dataclass semantics, see stub file desc.pyi.
    """
    return Descriptor(
        default=default,
        owner=owner,
        instance=instance,
        name=name,
        use_repr=use_repr,
        repr_func=repr_func,
        check_types=check_types,
        metadata=metadata,
        frozen=frozen,
        on_setattr=on_setattr,
    )
