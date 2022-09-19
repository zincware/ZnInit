"""ZnInit Package for automatic __init__ generation"""
from zninit.core import ZnInit
from zninit.descriptor import Descriptor, get_descriptors

__all__ = ("Descriptor", "ZnInit", "get_descriptors")
