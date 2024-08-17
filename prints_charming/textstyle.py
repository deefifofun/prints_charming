from dataclasses import dataclass
from typing import Optional


@dataclass
class TextStyle:

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


    def update(self, attributes):
        for attr, value in attributes.items():
            if hasattr(self, attr):
                setattr(self, attr, value)
