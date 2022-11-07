"""ZnInit Package for automatic __init__ generation"""
import importlib.metadata

from zninit.core import ZnInit
from zninit.descriptor import Descriptor, Empty, get_descriptors

__all__ = ("Descriptor", "ZnInit", "get_descriptors", "Empty")

__version__ = importlib.metadata.version("zninit")
