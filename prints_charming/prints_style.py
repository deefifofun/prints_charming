from dataclasses import dataclass, field, fields
from typing import Optional, Dict, Any


@dataclass
class PStyle:

    """
    A class to manage text styles including color, background color, and various text effects.
    """

    color: Optional[str] = 'default'
    bg_color: Optional[str] = None
    reverse: bool = False
    bold: bool = False
    dim: bool = False
    italic: bool = False
    underline: bool = False
    overline: bool = False
    strikethru: bool = False
    conceal: bool = False
    blink: bool = False


    def add_attributes(self, new_attributes: Dict[str, Any]):
        for attr, default_value in new_attributes.items():
            if not hasattr(self, attr):
                setattr(self, attr, default_value)


    def update(self, attributes):
        for attr, value in attributes.items():
            if hasattr(self, attr):
                setattr(self, attr, value)

    def remove_attributes(self, attributes: list):
        for attr in attributes:
            if hasattr(self, attr):
                delattr(self, attr)

    def get_all_attributes_with_types(self):
        attribs = {}
        # Iterate over dataclass fields (for predefined attributes)
        for field in fields(self):
            attribs[field.name] = type(getattr(self, field.name)).__name__

        # Also include dynamically added attributes
        for key, value in self.__dict__.items():
            if key not in attribs:
                attribs[key] = type(value).__name__

        return attribs
