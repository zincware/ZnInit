[![Coverage Status](https://coveralls.io/repos/github/zincware/ZnInit/badge.svg?branch=main)](https://coveralls.io/github/zincware/ZnInit?branch=main)
![PyTest](https://github.com/zincware/ZnInit/actions/workflows/pytest.yaml/badge.svg)
[![PyPI version](https://badge.fury.io/py/zninit.svg)](https://badge.fury.io/py/zninit)
[![code-style](https://img.shields.io/badge/code%20style-black-black)](https://github.com/psf/black/)
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/zincware/ZnInit/HEAD)
[![zincware](https://img.shields.io/badge/Powered%20by-zincware-darkcyan)](https://github.com/zincware)

# ZnInit - Automatic Generation of ``__init__`` based on Descriptors

This package provides a base class for ``dataclass`` like structures with the addition of using [Descriptors](https://docs.python.org/3/howto/descriptor.html).
The main functionality is the automatic generation of an keyword-only``__init__`` based on selected descriptors.
The descriptors can e.g. overwrite ``__set__`` or ``__get__`` or have custom metadata associated with them.
The ``ZnInit`` package is used by [ZnTrack](https://github.com/zincware/ZnTrack) to enable lazy loading data from files as well as distinguishing between different types of descriptors such as `zn.params` or `zn.outputs`. An example can be found in the `examples` directory.

# Example
The most simple use case is a replication of a dataclass like structure.

```python
from zninit import ZnInit, Descriptor


class Human(ZnInit):
    name: str = Descriptor()
    language: str = Descriptor("EN")


# This will generate the following init:
def __init__(self, *, name, language="EN"):
    self.name = name
    self.language = language


fabian = Human(name="Fabian")
# or
fabian = Human(name="Fabian", language="DE")
```

The benefit of using ``ZnInit`` comes with using descriptors. You can subclass the `zninit.Descriptor` class and only add certain kwargs to the `__init__` defined in `init_descriptors: list`. Furthermore, a `post_init` method is available to run code immediately after initializing the class.

````python
from zninit import ZnInit, Descriptor


class Input(Descriptor):
    """A Parameter"""


class Metric(Descriptor):
    """An Output"""


class Human(ZnInit):
    _init_descriptors_ = [Input] # only add Input descriptors to the __init__
    name: str = Input()
    language: str = Input("DE")
    date: str = Metric()  # will not appear in the __init__

    def _post_init_(self):
        self.date = "2022-09-16"


julian = Human(name="Julian")
print(julian) # Human(language='DE', name='Julian')
print(julian.date)  # 2022-09-16
print(Input.get_dict(julian)) # {"name": "Julian", "language": "DE"}
````
One benefit of ``ZnInit`` is that it also allows for inheritance.

````python
from zninit import ZnInit, Descriptor

class Animal(ZnInit):
    age: int = Descriptor()
    
class Cat(Animal):
    name: str = Descriptor()
    
billy = Cat(age=4, name="Billy")
````
