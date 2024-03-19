from typing import Any, Callable, Optional, TypeVar, overload, Literal

from zninit.descriptor import _Empty_TYPE

_T = TypeVar("_T")

# In reality, desc returns a Descriptor object. We lie about this
# and pretend it returns an object of the type of the managed attribute
# to enable dataclass semantics with type checkers, i.e.:
#
# class Human(ZnInit):
#     age: int = desc(0)

# If no default value is given, we pretend the return type is Any.
# The actual type will be inferred from the annotation in the class.
@overload
def desc(
    default: Literal[_Empty_TYPE.Empty] = ...,
    owner=...,
    instance=...,
    name=...,
    use_repr: bool = ...,
    repr_func: Callable = ...,
    check_types: bool = False,
    metadata: Optional[dict] = ...,
    frozen: bool = False,
    on_setattr: Optional[Callable] = ...,
) -> Any: ...

# If a default value is given, we pretend its type is the return type.
@overload
def desc(
    default: _T,
    owner=...,
    instance=...,
    name=...,
    use_repr: bool = ...,
    repr_func: Callable = ...,
    check_types: bool = False,
    metadata: Optional[dict] = ...,
    frozen: bool = False,
    on_setattr: Optional[Callable] = ...,
) -> _T: ...
