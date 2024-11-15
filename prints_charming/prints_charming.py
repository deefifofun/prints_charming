# prints_charming.py

import time
import os
import sys
import copy
import traceback
import re
import logging
import inspect
from datetime import datetime
from dataclasses import dataclass, asdict
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from .exceptions.base_exceptions import PrintsCharmingException

from .exceptions.internal_exceptions import (
    InvalidLengthError,
    ColorNotFoundError
)

from .prints_charming_defaults import (
    DEFAULT_CONFIG,
    DEFAULT_COLOR_MAP,
    DEFAULT_EFFECT_MAP,
    DEFAULT_UNICODE_MAP,
    DEFAULT_STYLES,
    DEFAULT_LOGGING_STYLES,
    DEFAULT_CONTROL_MAP
)

from .prints_style import PStyle
from .utils import compute_bg_color_map
from .trie_manager import KeyTrie
from .formatter import Formatter
from .internal_logging_utils import shared_logger

if sys.platform == 'win32':
    from .win_utils import WinUtils






class PrintsCharming:
    """
    The `PrintsCharming` class is the core component of the prints_charming
    library, a comprehensive terminal toolkit designed for advanced text
    styling, layouts, printing, and interactive console applications in Python.

    **Overview:**
    `PrintsCharming` provides advanced text styling capabilities, allowing
    developers to apply complex styles, manage configurations, and enhance
    console output with interactive elements.

    **Key Features:**

    - **Text Styling and Printing:**
      - Apply complex styles (colors, background colors, effects) to console output.
      - Define and manage custom styles using `PStyle` instances.
      - Style individual words, phrases, substrings, or entire blocks of text.
      - Support for dynamic and condition-based styling.

    - **Configuration Management:**
      - Manage shared configurations across instances for consistent styling.
      - Customize color maps, effect maps, and control codes.
      - Provide mechanisms for instance-specific overrides and customizations.

    **Note:**
    The `PrintsCharming` class serves as the foundation for other components
    within the library, such as logging, exception handling, tables, boxes,
    borders, interactive utilities, and more which build upon its
    functionalities to provide a cohesive toolkit for terminal applications.

    **Usage Example:**

    ```python
    pc = PrintsCharming()
    pc.print("Hello, PrintsCharming!", style="header")
    ```

    **Extensibility:**
    Designed with extensibility in mind, `PrintsCharming` allows developers to subclass
    and extend its capabilities to suit specific application needs.
    """

    RESET = "\033[0m"
    _TIMESTAMP_FORMAT = '%Y-%m-%d %H:%M:%S.%f'

    ansi_escape_pattern = re.compile(r'\033\[[0-9;]*[mK]')
    words_and_spaces_pattern = re.compile(r'\S+|\s+')

    # For package wide internal and subclass logging purposes.
    _shared_internal_logging_styles: Optional[Dict[str, PStyle]] = (
        copy.deepcopy(DEFAULT_LOGGING_STYLES)
    )

    _shared_instance = None
    _shared_instances = {}

    @classmethod
    def get_shared_instance(cls, key):
        """
        Retrieve a shared instance of PrintsCharming by key.

        This method allows for optional shared instances, where multiple instances of other modules
        (e.g., TableManager or FrameBuilder) can access the same PrintsCharming instance under a specified key.

        Args:
            key (str): The unique identifier associated with the shared instance.

        Returns:
            PrintsCharming: The shared PrintsCharming instance for the given key, or None if no instance is set for the key.

        Notes:
            - Using shared instances is entirely optional. These methods are provided for convenience
              when users want consistency across multiple instances of other modules.
            - For example, you might want all `TableManager` instances to share a single `PrintsCharming` instance
              under the key 'table_manager', while `FrameBuilder` instances could use a different instance
              under 'frame_builder'.
            - Users who prefer to manage `PrintsCharming` instances independently can bypass this feature
              entirely and manually pass instances to other modules as needed.
        """
        return cls._shared_instances.get(key)

    @classmethod
    def set_shared_instance(cls, key, instance):
        """
        Set a shared instance of PrintsCharming under a specific key.

        This method allows users to optionally store a shared instance that can be retrieved
        by other parts of the application, facilitating resource sharing across multiple modules or instances.

        Args:
            key (str): The unique identifier to associate with the instance.
            instance (PrintsCharming): The PrintsCharming instance to be stored for shared access.

        Notes:
            - This method is entirely optional. It is designed for users who want to share the same
              PrintsCharming instance across multiple instances of other modules.
            - For example, you may wish to set a shared instance for all `TableManager` objects
              by storing it under the key 'table_manager'. Likewise, a separate instance could be
              stored for `FrameBuilder` objects under a different key if desired.
            - This feature can be ignored entirely by users who prefer to create and pass individual
              PrintsCharming instances to each module as needed without storing them in `_shared_instances`.
        """
        cls._shared_instances[key] = instance


    log_level_style_names = ['debug', 'info', 'warning', 'error', 'critical']

    @classmethod
    def set_log_level_style_names(cls, levels) -> None:
        """
        Sets the log levels for the class.

        :param levels: A list of log level strings.
        """
        if (
            not isinstance(levels, list)
            or not all(isinstance(lvl, str) for lvl in levels)
        ):
            raise ValueError("log_levels must be a list of strings.")
        cls.log_levels = levels


    shared_color_map: Optional[Dict[str, str]] = None
    shared_bg_color_map: Optional[Dict[str, str]] = None
    shared_effect_map: Optional[Dict[str, str]] = DEFAULT_EFFECT_MAP
    shared_unicode_map: Optional[Dict[str, str]] = DEFAULT_UNICODE_MAP
    shared_styles: Optional[Dict[str, PStyle]] = None
    shared_ctl_map: Optional[Dict[str, str]] = DEFAULT_CONTROL_MAP


    @classmethod
    def set_shared_maps(cls,
                        shared_color_map: Optional[Dict[str, str]] = None,
                        shared_bg_color_map: Optional[Dict[str, str]] = None,
                        shared_effect_map: Optional[Dict[str, str]] = None,
                        shared_unicode_map: Optional[Dict[str, str]] = None,
                        shared_styles: Optional[Dict[str, PStyle]] = None,
                        shared_ctl_map: Optional[Dict[str, str]] = None
                        ) -> None:
        """
        Set shared maps across all instances of the PrintsCharming class.

        **Purpose:**
        The `set_shared_maps` method allows you to define shared configurations
        that are accessible by all instances of the PrintsCharming class. This
        method lets you establish a consistent set of color maps, styles, and
        effects that will be applied uniformly across all instances unless
        specifically overridden. This behavior is similar to having default
        configurations that other libraries might hardcode, but with the added
        flexibility that you can modify these shared configurations at runtime.

        **Flexibility & Power:**
        While this method allows you to set shared configurations that apply to
        all instances—similar to class-level defaults—PrintsCharming’s true
        strength lies in its flexibility. Unlike many similar libraries with
        rigid, predefined constants, PrintsCharming offers the freedom to
        configure each instance individually. This approach gives you the power
        to either enforce consistency across all instances or tailor the
        behavior and styling of text printing according to the specific needs
        of your application.

        **When to Use This Method:**
        - If you have a scenario where consistent styling or configurations are
          required or preferred across all instances, using `set_shared_maps`
          can be very powerful.
        - For many other cases, where instance-specific customization is more
          appropriate, you can skip this method altogether and rely on
          individual configurations for each instance.

        **Important Considerations:**
        - This method is an option, not a requirement. Use it when it makes
          sense for your project.
        - Shared maps set through this method will be applied to all future
          instances unless overridden in the instance's `__init__` method.

        **Parameters:**
        :param shared_color_map: (Optional) A dictionary of shared color
                                 mappings to be accessible globally across all
                                 instances. If not provided,
                                 `DEFAULT_COLOR_MAP.copy()` will be used.

        :param shared_bg_color_map: (Optional) A dictionary of shared
                                    background color mappings. to be accessible
                                    globally across all instances. If None
                                    (as it should be unless your really know
                                    what your doing), it will be computed from
                                    shared_color_map.

        :param shared_effect_map: (Optional) A dictionary of effect mappings.
                                  **This should not be changed unless you are
                                  certain of what you're doing.**

        :param shared_unicode_map: (Optional) A dictionary of unicode mappings.

        :param shared_styles: (Optional) A dictionary of shared styles. This
                              allows for the consistent application of text
                              styles across all instances.

        :param shared_ctl_map: (Optional) A dictionary of shared control codes.
        """

        cls.shared_color_map = shared_color_map or DEFAULT_COLOR_MAP.copy()
        cls.shared_color_map.setdefault('default', PrintsCharming.RESET)
        cls.shared_bg_color_map = shared_bg_color_map or {
            color: compute_bg_color_map(code)
            for color, code in cls.shared_color_map.items()
        }

        if shared_effect_map:
            cls.shared_effect_map = shared_effect_map

        if shared_unicode_map:
            cls.shared_unicode_map = shared_unicode_map

        if shared_styles:
            cls.shared_styles = shared_styles

        if shared_ctl_map:
            cls.shared_ctl_map = shared_ctl_map



    @classmethod
    def clear_line(cls, use_carriage_return: bool = True):
        if use_carriage_return:
            print("\r" + cls.shared_ctl_map["clear_line"], end='')
        else:
            print(cls.shared_ctl_map["clear_line"], end='')



    def __init__(self,
                 config: Optional[Dict[str, Union[bool, str, int]]] = None,
                 color_map: Optional[Dict[str, str]] = None,
                 bg_color_map: Optional[Dict[str, str]] = None,
                 default_bg_color: Optional[str] = None,
                 effect_map: Optional[Dict[str, str]] = None,
                 unicode_map: Optional[Dict[str, str]] = None,
                 styles: Optional[Dict[str, PStyle]] = None,
                 styled_strings: Optional[Dict[str, List[str]]] = None,
                 style_conditions: Optional[Any] = None,
                 formatter: Optional['Formatter'] = None,
                 autoconf_win: bool = False
                 ) -> None:

        """
        Initialize PrintsCharming with args to any of these optional params.

        :param config: enable or disable various functionalities of this class.

        :param color_map: supply your own color_map dictionary.
                          'color_name': 'ansi_code'

        :param bg_color_map: supply your own bg_color_map dictionary. Default
                             is computed from color_map dictionary.

        :param default_bg_color: change the default background color to a color
                                 other than your terminal's background color.

        :param effect_map: supply your own effect_map dictionary. Default is
                           PrintsCharming.shared_effect_map

        :param unicode_map: supply your own unicode_map dictionary. Default is
                            PrintsCharming.shared_unicode_map

        :param styles: supply your own styles dictionary. Default is a copy of
                       the DEFAULT_STYLES dictionary unless cls.shared_styles
                       is defined.

        :param styled_strings: calls the add_strings_from_dict method with your
                               provided styled_strings dictionary. See README
                               for more info.

        :param style_conditions: A custom class for implementing dynamic
                                 application of styles to text based on
                                 conditions.

        :param formatter: supply your own formatter class instance to be used
                          for formatting text printed using the print method in
                          this class.

        :param autoconf_win: If your using legacy windows cmd prompt and not
                             getting colored/styled text then change this to
                             True to make things work.
        """

        self.config = {**DEFAULT_CONFIG, **(config or {})}

        self.color_map = (
            color_map
            or PrintsCharming.shared_color_map
            or DEFAULT_COLOR_MAP.copy()
        )
        self.color_map.setdefault('default', PrintsCharming.RESET)

        self.bg_color_map = (
            bg_color_map
            or PrintsCharming.shared_bg_color_map
            or {
                color: compute_bg_color_map(code)
                for color, code in self.color_map.items()
            }
        )

        self.effect_map = effect_map or PrintsCharming.shared_effect_map

        self.unicode_map = unicode_map or PrintsCharming.shared_unicode_map

        self.ctl_map = self.shared_ctl_map

        self.styles = (
            copy.deepcopy(styles)
            or PrintsCharming.shared_styles
            or copy.deepcopy(DEFAULT_STYLES)
        )

        self.default_bg_color = default_bg_color

        if default_bg_color is not None and default_bg_color in self.bg_color_map:
            for style_key, style_value in self.styles.items():
                if (
                    not hasattr(style_value, 'bg_color')
                    or getattr(style_value, 'bg_color') is None
                ):
                    setattr(style_value, 'bg_color', default_bg_color)

        self.style_codes: Dict[str, str] = {
            name: self.create_style_code(style)
            for name, style in self.styles.items()
            if self.styles[name].color in self.color_map
        }


        self._internal_logging_styles = (
            PrintsCharming._shared_internal_logging_styles
        )


        self._internal_logging_style_codes: Dict[str, str] = {
            name: self.create_style_code(style)
            for name, style in self._internal_logging_styles.items()
            if (
                self._internal_logging_styles[name].color in self.color_map
            )
        }

        self.reset = PrintsCharming.RESET

        self.conceal_map: Dict[str, Dict[str, str]] = {}

        self.phrase_trie = KeyTrie()
        self.shortest_phrase_length = None
        self.word_trie = KeyTrie()
        self.word_map: Dict[str, Dict[str, str]] = {}
        self.subword_trie = KeyTrie()

        self.enable_conceal_map = False
        self.enable_styled_phrases = False
        self.enable_styled_words = False
        self.enable_word_trie = False
        self.enable_word_map = False
        self.enable_styled_subwords = False
        self.enable_styled_variable_map = False

        self.sentence_ending_characters = ".,!?:;"


        if styled_strings:
            self.add_strings_from_dict(styled_strings)

        self.style_conditions = style_conditions
        self.style_conditions_map = {}
        if style_conditions:
            self.style_conditions_map = style_conditions.map

        self.style_cache = {}

        if sys.platform == 'win32':
            self.win_utils = WinUtils
            if autoconf_win and not WinUtils.is_ansi_supported_natively():
                if not WinUtils.enable_win_console_ansi_handling():
                    logging.error("Failed to enable ANSI handling on Windows")

        # Instance-level flag to control logging
        self.internal_logging_enabled = (
            self.config.get("internal_logging", False)
        )

        # Use shared logger but don't disable it
        self.logger = shared_logger
        self.setup_internal_logging(self.config.get("log_level", "DEBUG"))

        self.formatter = formatter or Formatter()



    def escape_ansi_codes(self, ansi_string):
        self.debug(
            "Escaping ANSI codes in string: {}",
            ansi_string
        )
        escaped_ansi_string = ansi_string.replace("\033", "\\033")
        self.debug(
            "Escaped ANSI codes in string: {}",
            escaped_ansi_string
        )

        return escaped_ansi_string


    def create_style_code(self, style: Union[PStyle, Dict[str, Any]]):
        style_codes = []

        if isinstance(style, PStyle):
            # Add foreground color
            if style.color and style.color in self.color_map:
                style_codes.append(self.color_map[style.color])

            # Add background color if provided
            if style.bg_color and style.bg_color in self.bg_color_map:
                style_codes.append(self.bg_color_map[style.bg_color])

            # Loop through other attributes
            for attr, ansi_code in self.effect_map.items():
                if getattr(style, attr, False):
                    style_codes.append(ansi_code)

        elif isinstance(style, Dict):
            # Add foreground color
            if "color" in style and style["color"] in self.color_map:
                style_codes.append(self.color_map[style["color"]])

            # Add background color if provided
            if "bg_color" in style and style["bg_color"] in self.bg_color_map:
                style_codes.append(self.bg_color_map[style["bg_color"]])

            # Loop through other effects
            for effect, ansi_code in self.effect_map.items():
                if effect in style and style[effect]:
                    style_codes.append(ansi_code)

        return "".join(style_codes)


    def add_style(self, name: str, style: PStyle):
        """
        Add a new style, applying self.default_bg_color only if no bg_color is specified
        and self.default_bg_color is defined.
        """

        # Apply default background color if none is specified and self.default_bg_color is set
        if (not hasattr(style, 'bg_color') or style.bg_color is None) and self.default_bg_color:
            style.bg_color = self.default_bg_color

        # Add the style and generate the style code if the color is in the color map
        self.styles[name] = style
        if self.styles[name].color in self.color_map:
            style_code = self.create_style_code(self.styles[name])
            self.style_codes[name] = style_code


    def add_styles(self, styles: dict[str, PStyle]) -> None:
        """
        Add multiple styles, applying self.default_bg_color only if no bg_color is specified
        and self.default_bg_color is defined.
        """
        for style_name, style in styles.items():
            # Apply default background color if none is specified and self.default_bg_color is set
            if (not hasattr(style, 'bg_color') or style.bg_color is None) and self.default_bg_color:
                style.bg_color = self.default_bg_color

            if style.color in self.color_map:
                self.add_style(style_name, style)


    def edit_style(self, name: str, new_style: Union[PStyle, Dict[str, Any]]):
        """
        Edit an existing style by updating its attributes and regenerating its ANSI code,
        applying the default background color if not specified.
        """
        if name not in self.styles:
            raise ValueError(f"Style '{name}' does not exist.")

        # Update the style with new attributes
        if isinstance(new_style, PStyle):
            self.styles[name] = new_style
        elif isinstance(new_style, Dict):
            for key, value in new_style.items():
                if hasattr(self.styles[name], key):
                    setattr(self.styles[name], key, value)
                else:
                    raise AttributeError(f"Style '{name}' has no attribute '{key}'")

        # Ensure the background color respects the default if not specified
        if getattr(self.styles[name], 'bg_color', None) is None and self.default_bg_color:
            self.styles[name].bg_color = self.default_bg_color

        # Regenerate the ANSI code for the updated style
        self.style_codes[name] = self.create_style_code(self.styles[name])


    def edit_styles(self, new_styles: Dict[str, Union[PStyle, Dict[str, Any]]]):
        """
        Edit multiple styles by updating each style's attributes and regenerating their ANSI codes,
        applying the default background color if not specified.
        """
        for name, new_style in new_styles.items():
            if name not in self.styles:
                raise ValueError(f"Style '{name}' does not exist.")

            # Use edit_style to apply the default background color as necessary
            self.edit_style(name, new_style)


    def rename_style(self, current_name: str, new_name: str):
        """
        Rename an existing style in both self.styles and self.style_codes.
        """
        if current_name not in self.styles:
            raise ValueError(f"Style '{current_name}' does not exist.")
        if new_name in self.styles:
            raise ValueError(f"Style '{new_name}' already exists.")

        # Move style and its code to the new name
        self.styles[new_name] = self.styles.pop(current_name)
        if current_name in self.style_codes:
            self.style_codes[new_name] = self.style_codes.pop(current_name)


    def rename_styles(self, name_map: dict[str, str]):
        """
        Rename multiple styles using a mapping from current names to new names.
        """
        for current_name, new_name in name_map.items():
            self.rename_style(current_name, new_name)


    def remove_style(self, name: str):
        """
        Remove a style by its name from both self.styles and self.style_codes.
        """
        if name in self.styles:
            del self.styles[name]
            if name in self.style_codes:
                del self.style_codes[name]
        else:
            raise ValueError(f"Style '{name}' does not exist.")


    def remove_styles(self, names: list[str]):
        """
        Remove multiple styles by their names from both self.styles and self.style_codes.
        """
        for name in names:
            self.remove_style(name)


    def get_style_code(self, style_name):
        return self.style_codes.get(style_name, self.style_codes['default'])


    def apply_style_code(self, code, text, reset=True):
        return f'{code}{text}{self.reset if reset else ''}'


    def apply_style(self, style_name, text, fill_space=True, reset=True):
        self.debug(
            "Applying style_name: {} to text: {}",
            self._apply_style_internal('info', style_name),
            self._apply_style_internal('info', text)
        )
        self.debug(
            "Applying style_name: %s to text: %s",
            self._apply_style_internal('info', style_name),
            self._apply_style_internal('info', text))

        text = str(text)
        if text.isspace() and fill_space:
            style_code = self.bg_color_map.get(
                style_name,
                self.bg_color_map.get(
                    self.styles.get(style_name, 'default_bg').bg_color
                )
            )

        else:
            style_code = self.style_codes.get(
                style_name,
                self.color_map.get(
                    style_name,
                    self.color_map.get('default')
                )
            )

        styled_text = f"{style_code}{text}{self.reset if reset else ''}"

        escaped_string = self.escape_ansi_codes(styled_text)
        self.debug('escaped_string: {}', escaped_string)
        self.debug(styled_text)

        return styled_text




    def apply_indexed_styles(self, strs_list, styles_list, return_list=False):
        strings_list_len = len(strs_list)

        # If a single style string is passed, repeat it for the entire list
        if isinstance(styles_list, str):
            styles_list = [styles_list] * strings_list_len

        # If a list of styles is passed
        elif isinstance(styles_list, list):
            if len(styles_list) < strings_list_len:
                # Repeat styles_list pattern until it matches len of strs_list
                styles_list = (
                    styles_list * (strings_list_len // len(styles_list) + 1)
                )[:strings_list_len]

        # Apply the styles to the strings
        styled_strs = [
            self.apply_style(style, str(text))
            for style, text in zip(styles_list, strs_list)
        ]

        # Return either the list of styled strings or a joined string
        return ' '.join(styled_strs) if not return_list else styled_strs





    def get_color_code(self, color_name):
        return self.color_map.get(color_name, self.color_map['default'])


    def apply_color(self, color_name, text, fill_space=True):

        text = str(text)
        if text.isspace() and fill_space:
            color_code = self.bg_color_map.get(
                color_name,
                'default'
            )
        else:
            color_code = self.color_map[color_name]

        colored_text = f"{color_code}{text}{self.reset}"

        return colored_text


    def get_bg_color_code(self, color_name):
        return self.bg_color_map.get(color_name)


    def apply_bg_color(self, color_name, text):
        bg_color_code = self.get_bg_color_code(color_name)
        bg_color_block = f"{bg_color_code}{text}{self.reset}"

        return bg_color_block


    def generate_bg_bar_strip(self, color_name: str, length: int = 10) -> str:
        """
        Generates a block of background color as a string.

        :param color_name: The name of the color as per self.color_map.
        :param length: The length of the color block in terms of spaces.
        :raises ColorNotFoundError: If the background color is not found in
                                    the background color map.
        :raises InvalidLengthError: If the length is not valid.
        """
        self.debug(
            "Printing background color: {} with length: {}",
            color_name,
            length
        )

        if length <= 0:
            message = f"Invalid length '{length}'. Length must be positive."
            styled_message = self.apply_style('vred', message)
            raise InvalidLengthError(styled_message,
                                     self,
                                     format_specific_exception=True)

        bg_color_code = self.bg_color_map.get(color_name)
        if not bg_color_code:
            message = f"Key '{color_name}' not in 'self.bg_color_map'."
            styled_message = self.apply_style('vred', message)
            raise ColorNotFoundError(styled_message,
                                     self,
                                     format_specific_exception=True)

        # style the color block
        bg_bar_strip = f"{bg_color_code}{' ' * length}{self.reset}"

        return bg_bar_strip


    def print_bg_bar_strip(self, color_name: str, length: int = 10) -> None:
        """Prints a block of background color."""
        try:
            bg_bar_strip = self.generate_bg_bar_strip(color_name, length)
            print(bg_bar_strip)
        except (ColorNotFoundError, InvalidLengthError) as e:
            e.handle_exception()


    def get_effect_code(self, effect_name):
        return self.effect_map.get(effect_name, '')


    def apply_effect(self, effect_name, text):
        effect_code = self.get_effect_code(effect_name)
        return f'{effect_code}{text}{self.reset}'


    def add_subword(self, subword: str, style_name: str) -> None:
        """
        Adds a subword to the subword trie with a specific style.

        :param subword: The subword to be styled.
        :param style_name: The name of the style to apply.
        """

        subword = str(subword)
        if style_name in self.styles:

            # Get the style attributes
            attribs = vars(self.styles.get(style_name)).copy()
            if attribs.get('reversed'):
                attribs['color'], attribs['bg_color'] = (
                    attribs.get('bg_color'), attribs.get('color')
                )

            # Insert the subword into the subword trie
            self.subword_trie.insert(subword, {
                "style": style_name,
                "style_code": self.style_codes[style_name],
                "attribs": attribs
            })

            # Enable the subwords flag
            if not self.enable_styled_subwords:
                self.enable_styled_subwords = True
        else:
            print(f"Style {style_name} not found in styles dictionary.")

    def add_string(self,
                   string: str,
                   style_name: str,
                   word_trie: bool = False
                   ) -> None:
        """
        Adds a string (word or phrase) to the appropriate trie with a specific
        style.

        :param string: The string to be styled.
        :param style_name: The name of the style to apply.
        :param word_trie: Insert in word_trie if True otherwise word_map
        """

        string = str(string)
        if style_name in self.styles:
            style_code = self.get_style_code(style_name)
            styled_string = f"{style_code}{string}{self.reset}"

            # Copy the style attributes
            attribs = vars(self.styles.get(style_name)).copy()
            if attribs.get('reversed'):
                attribs['color'], attribs['bg_color'] = (
                    attribs.get('bg_color'), attribs.get('color')
                )

            # Handle concealment separately if needed
            if style_name == 'conceal':
                self.conceal_map[string] = {
                    "style": style_name,
                    "styled": styled_string
                }
                if not self.enable_conceal_map:
                    self.enable_conceal_map = True
                return

            # Determine if the string is a phrase (contains inner spaces)
            contains_inner_space = ' ' in string.strip()

            if contains_inner_space:
                # Insert the phrase into the phrase trie
                phrase_words_and_spaces = (
                    PrintsCharming.words_and_spaces_pattern.findall(string)
                )
                phrase_length = len(phrase_words_and_spaces)
                if not self.shortest_phrase_length:
                    self.shortest_phrase_length = phrase_length
                else:
                    if phrase_length < self.shortest_phrase_length:
                        self.shortest_phrase_length = phrase_length
                self.phrase_trie.insert(string, {
                    "phrase_words_and_spaces": phrase_words_and_spaces,
                    "phrase_length": phrase_length,
                    "style": style_name,
                    "style_code": style_code,
                    "styled": styled_string,
                    "attribs": attribs
                })
                if not self.enable_styled_phrases:
                    self.enable_styled_phrases = True
            else:
                if word_trie:
                    # Insert the word into the word trie
                    self.word_trie.insert(string, {
                        "style": style_name,
                        "style_code": style_code,
                        "styled": styled_string,
                        "attribs": attribs
                    })
                    if not self.enable_styled_words:
                        self.enable_styled_words = True
                    if not self.enable_word_trie:
                        self.enable_word_trie = True
                else:
                    # Insert the word into the word map
                    self.word_map[string] = {
                        "style": style_name,
                        "style_code": style_code,
                        "styled": styled_string,
                        "attribs": attribs
                    }
                    if not self.enable_styled_words:
                        self.enable_styled_words = True
                    if not self.enable_word_map:
                        self.enable_word_map = True

        else:
            print(f"Style {style_name} not found in styles dictionary.")


    def add_strings(self,
                    strings: List[str],
                    style_name: str,
                    word_trie: bool = False
                    ) -> None:
        """
        Adds a list of strings (can be a mix of phrases and words) to an
        instance trie or dictionary depending on if it is a phrase (contains
        one or more ' ' characters) then will be added to self.phrase_trie or
        if it is a word (does not contain any ' ' characters) then it is added
        to self.word_map unless word_trie param is set to True which in that
        case the word will be added to self.word_trie.
        """
        if style_name in self.styles:
            style_code = self.style_codes[style_name]
            for string in strings:
                self.add_string(string, style_name, word_trie)


    def add_strings_from_dict(self,
                              strings_dict: Dict[str, List[str]],
                              word_trie: bool = False,
                              ) -> None:
        """
        Adds strings (can be a mix of phrases and words) to an instance trie or
        dictionary depending on if it is a phrase (contains one or more ' '
        characters) then will be added to self.phrase_trie or if it is a word
        (does not contain any ' ' characters) then it is added to
        self.word_map unless word_trie param is set to True which in that case
        the word will be added to self.word_trie.
        """
        for style_name, strings in strings_dict.items():
            if style_name in self.styles:
                self.add_strings(strings, style_name, word_trie)
            else:
                print(f"Style {style_name} not found in styles dictionary.")


    def remove_string(self, string: str) -> None:
        """
        Removes a string (word or phrase) from the appropriate trie, and
        handles concealment.

        :param string: The string to be removed.
        """

        string = str(string)

        # Determine if the string is a phrase (contains inner spaces)
        contains_inner_space = ' ' in string.strip()

        if contains_inner_space:
            # Remove from the phrase trie if present
            if (
                self.phrase_trie
                and self._remove_from_trie(self.phrase_trie, string)
            ):
                print(f"Removed '{string}' from phrase trie")

        else:

            if self.enable_word_trie:
                # Remove from the word trie if present
                if (
                    self.word_trie
                    and self._remove_from_trie(self.word_trie, string)
                ):
                    print(f"Removed '{string}' from word trie")

            if self.enable_word_map:
                # Remove from the word map if present
                if self.word_map and self._remove_word(string):
                    print(f"Removed '{string}' from word map")

            # Remove from the conceal_map if present
            if string in self.conceal_map:
                del self.conceal_map[string]
                print(f"Removed '{string}' from conceal map")


    def _remove_from_trie(self, trie: KeyTrie, string: str) -> bool:
        """
        Removes a string from the trie by marking the end node as non-terminal
        (is_end = False). It does not remove the nodes themselves, because they
        may be shared with other words/phrases.

        :param trie: The trie to remove the string from.
        :param string: The string to remove.
        :return: True if the string was removed, False if the string was not
                 found.
        """
        node = trie.root
        stack = []  # To keep track of the path

        # Traverse the trie to find the string
        for char in string:
            if char not in node.children:
                return False  # String not found in trie
            stack.append((node, char))  # Store the parent node and char
            node = node.children[char]

        # Check if we reached the end of a valid word/phrase
        if node.is_end:
            # Mark the node as non-terminal
            node.is_end = False
            node.style_info = None  # Optionally clear style information

            # Clean up unused nodes if they are not part of other words/phrases
            self._cleanup_trie(stack)

            return True
        return False  # String was not found as a complete word/phrase

    @staticmethod
    def _cleanup_trie(stack):
        """
        Recursively clean up the trie by removing nodes that are no longer part
        of any valid words/phrases.

        :param stack: A list of (node, char) pairs that represent the path of
                      the string in the trie.
        """
        while stack:
            node, char = stack.pop()
            child_node = node.children[char]

            # If the child node has no children and is not the end of another
            # word/phrase, remove it.
            if not child_node.children and not child_node.is_end:
                del node.children[char]
            else:
                # If the child node has children or marks the end of another
                # word/phrase, stop cleaning.
                break


    def _remove_word(self, word: str) -> bool:
        if word in self.word_map:
            del self.word_map[word]
            return True
        elif word in self.conceal_map[word]:
            del self.conceal_map[word]
            return True
        return False



    def conceal_text(self, text_to_conceal, replace=False, style_name=None):
        if replace:
            style_code = self.get_style_code(style_name)
            if not style_code:
                style_code = self.style_codes.get('default')
            concealed_text = f"{style_code}***concealed_text***{self.reset}"
        else:
            style_code = self.style_codes.get('conceal')
            if not style_code:
                style_code = PrintsCharming.shared_effect_map.get('conceal')
            concealed_text = f"{style_code}{text_to_conceal}{self.reset}"

        return concealed_text


    def format_dict(self, d, indent=4) -> str:
        """
        Formats a dictionary as a styled string.

        :param d: The dictionary to format.
        :param indent: The number of spaces to use for indentation.
        :return: A string representing the formatted dictionary.
        """

        def pprint_dict(d, level=0):
            result = ""
            for key, value in d.items():
                result += (
                    " " * (level * indent)
                    + self.apply_style('dict_key', f"{key}: ")
                )
                if isinstance(value, dict):
                    result += (
                        "{\n"
                        + pprint_dict(value, level + 1)
                        + " " * (level * indent)
                        + "}\n"
                    )
                elif isinstance(value, bool):
                    bool_style = 'true' if value else 'false'
                    result += (
                        self.apply_style(bool_style, str(value))
                        + "\n"
                    )
                elif value is None:
                    result += (
                        self.apply_style('none', str(value))
                        + "\n"
                    )
                elif isinstance(value, int):
                    result += (
                        self.apply_style('int', str(value))
                        + "\n"
                    )
                elif isinstance(value, float):
                    result += (
                        self.apply_style('float', str(value))
                        + "\n"
                    )
                elif (
                    isinstance(value, str)
                    and value.isupper()
                    and value.lower() in self.__class__.log_level_style_names
                ):
                    result += (
                        self._apply_style_internal(value.lower(), str(value))
                        + "\n"
                    )
                else:
                    result += f"{value}\n"
            return result

        return "{\n" + pprint_dict(d) + "}"


    def segment_with_splitter_and_style(self,
                                        text: str,
                                        splitter_match: str,
                                        splitter_swap: Union[str, bool],
                                        splitter_show: bool,
                                        splitter_style: Union[str, List[str]],
                                        splitter_arms: bool,
                                        string_style: List[str]
                                        ) -> str:
        """
        Segments a text string using a specified splitter, applies style to
        each segment and splitter, and returns the styled result.

        This method splits `text` based on `splitter_match`, applies a list of
        styles to each segment and optionally to the splitter, then reassembles
        and returns the styled text.

        Parameters:
            text (str): The text to be segmented and styled.
            splitter_match (str): The string that identifies where to split `text`.
            splitter_swap (Union[str, bool]): The string to replace the splitter with;
                if set to False, `splitter_match` is used as the splitter.
            splitter_show (bool): Determines if the splitter should be included in
                the output between segments.
            splitter_style (Union[str, List[str]]): A single style or list of styles
                to apply to the splitter; if a list is provided, styles rotate
                across instances of the splitter.
            splitter_arms (bool): If True, applies styles to both the splitter
                and padding around it.
            string_style (List[str]): List of styles to apply to each segment;
                styles rotate across segments if the list length is shorter than
                the number of segments.

        Returns:
            str: The fully assembled, styled text with segments and splitters
            styled according to the parameters.

        """
        if isinstance(splitter_style, str):
            splitter_styles = [splitter_style]
        else:
            splitter_styles = splitter_style

        # Determine the actual splitter to use
        actual_splitter = splitter_swap if splitter_swap else splitter_match

        # Split the text based on the splitter_match
        segments = text.split(splitter_match)
        styled_segments = []

        for i, segment in enumerate(segments):
            # Apply string style to the segment
            segment_style = (
                string_style[i % len(string_style)]
                if string_style else 'default'
            )
            styled_segment = (
                f"{self.style_codes[segment_style]}{segment}{self.reset}"
            )
            #styled_segment = segment  # Start with the original segment

            if splitter_show and i > 0:

                if len(splitter_styles) == 1:
                    styled_splitter = (
                        f"{self.style_codes[splitter_styles[0]]}"
                        f"{actual_splitter}{self.reset}"
                    )
                else:
                    splitter_len = len(splitter_styles)
                    styled_splitter = (
                        f"{self.style_codes[splitter_styles[i % splitter_len]]}"
                        f"{actual_splitter}{self.reset}"
                    )
                    #styled_segment = styled_splitter + styled_segment

                # Apply the appropriate style to the splitter and padding
                if splitter_arms:
                    styled_segment = styled_splitter + styled_segment
                else:
                    styled_segment = actual_splitter + styled_segment

            styled_segments.append(styled_segment)

        return ''.join(styled_segments)

    # breaking changes i need to fix and combine with another one of these methods.
    def segment_and_style2(self,
                           text: str,
                           styles_dict: Dict[str, Union[str, int, List[Union[str, int]]]]
                           ) -> str:
        """
        Segments the input text and applies specified styles to words based on
        indices or word matches provided in a styles dictionary.

        This method splits the `text` into words, then applies styling to specific
        words according to `styles_dict`, where each style is associated with either
        word indices or word content. Optionally, a final style can be applied to
        any words not styled by previous operations.

        Parameters:
            text (str): The input text to be segmented and styled.
            styles_dict (Dict[str, Union[str, int, List[Union[str, int]]]]):
                A dictionary mapping styles to indices or words. Each key is a style,
                and each value indicates the words to style with that style.
                - If the value is an integer, it represents a 1-based index of a word
                  in `text` to style with the key's style.
                - If the value is a list, it can contain a mix of integers (1-based
                  indices) and words, where each item specifies words to style with
                  the corresponding key.
                - If the value is an empty string (""), the style will be applied as
                  the final style to any remaining unstyled words.

        Returns:
            str: The fully styled text, with each word styled according to the
            mappings specified in `styles_dict`.

        Example:
            Given `text = "This is a sample text"` and
            `styles_dict = {"bold": [1, "sample"], "italic": "", "underline": 3}`,
            the method will:
            - Apply "bold" style to the 1st word and the word "sample".
            - Apply "underline" style to the 3rd word.
            - Apply "italic" style to any remaining unstyled words.

        """
        words = text.split()
        word_indices = {word: i for i, word in enumerate(words)}  # Map words to their indices
        operations = []

        final_style = None

        # Prepare operations by iterating over the styles_dict
        for style, value in styles_dict.items():
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, int):
                        operations.append((item - 1, style))  # Convert 1-based index to 0-based
                    elif item in word_indices:
                        operations.append((word_indices[item], style))
            else:
                if isinstance(value, int):
                    operations.append((value - 1, style))  # Convert 1-based index to 0-based
                elif value in word_indices:
                    operations.append((word_indices[value], style))
                elif value == '':  # Handle the final style indicated by an empty string
                    final_style = style

        # Sort operations by index
        operations.sort()

        # Initialize the styled words with the entire text unstyled
        styled_words = words.copy()

        # Apply styles in the correct order
        for i, (index, style) in enumerate(operations):
            prev_index = operations[i - 1][0] + 1 if i > 0 else 0
            for j in range(prev_index, index + 1):
                styled_words[j] = f"{self.style_codes[style]}{words[j]}{self.reset}"

        # Apply the final style to any remaining words after the last operation
        if final_style:
            last_index = operations[-1][0] if operations else 0
            for j in range(last_index + 1, len(words)):
                styled_words[j] = f"{self.style_codes[final_style]}{words[j]}{self.reset}"

        return " ".join(styled_words)



    def segment_and_style(self,
                          text: str,
                          styles_dict: Dict[str, Union[str, int]]
                          ) -> str:
        """
        Segments the input text and applies specified styles to words based on
        indices or word matches from a dictionary of styles.

        This method divides `text` into individual words, then iterates over
        `styles_dict` to apply styles to specific words, based on either their
        index or content. Additionally, a final style can be applied to all
        remaining words after the last specified index or match.

        Parameters:
           text (str): The input text to be segmented and styled.
           styles_dict (Dict[str, Union[str, int]]): A dictionary where each key
               is a style to apply, and each value specifies either the index
               or the word in `text` to which the style should be applied.
               - If the value is an integer, it represents a 1-based index of the
                 word in `text` to style with the corresponding style.
               - If the value is a string, it matches the word in `text` to style
                 with the corresponding style.
               - If the value is an empty string or `None`, the style will be applied
                 as the final style to all remaining unstyled words in `text`.

        Returns:
           str: The fully styled text, with each word styled according to the
           mappings specified in `styles_dict`.

        Example:
           Given `text = "This is a sample text"` and
           `styles_dict = {"bold": 1, "italic": "sample", "underline": ""}`,
           the method will:
           - Apply "bold" style to the 1st word ("This").
           - Apply "italic" style to the word "sample".
           - Apply "underline" style to any remaining words after "sample".

        """
        words = text.split()
        previous_index = 0
        value_style = None

        # Iterate over the styles_dict items
        for style, key in styles_dict.items():
            if key:  # If key is provided (not an empty string or None)
                if isinstance(key, int):  # Handle key as an index
                    key_index = key - 1  # Convert 1-based index to 0-based
                else:  # Handle key as a word (string)
                    try:
                        key_index = words.index(str(key), previous_index)
                    except ValueError:
                        continue  # If key is not found, skip to the next item

                # Apply the style to the words between previous_index and key_index
                for i in range(previous_index, key_index):
                    words[i] = f"{self.style_codes[style]}{words[i]}{self.reset}"

                # Apply the style to the key word itself
                words[key_index] = f"{self.style_codes[style]}{words[key_index]}{self.reset}"

                # Update previous_index to the current key_index + 1 for the next iteration
                previous_index = key_index + 1
            else:
                # This handles the case where the key is empty, meaning style from the last key to the end
                value_style = style

        # Apply the final style to the remaining words after the last key
        if value_style:
            for i in range(previous_index, len(words)):
                words[i] = f"{self.style_codes[value_style]}{words[i]}{self.reset}"

        return " ".join(words)

    # Work in progress made some breaking changes i need to correct.
    def segment_and_style_update(self, text: str, styles_dict: Dict[str, Union[str, int]]) -> str:
        """
        Segments the input text and applies specified styles to words based on
        indices or word matches from a dictionary of styles.

        This method divides `text` into individual words and spaces, then iterates over
        `styles_dict` to apply styles to specific words, based on either their
        index or content. Additionally, a final style can be applied to all
        remaining words after the last specified index or match.

        Parameters:
           text (str): The input text to be segmented and styled.
           styles_dict (Dict[str, Union[str, int]]): A dictionary where each key
               is a style to apply, and each value specifies either the index
               or the word in `text` to which the style should be applied.
               - If the value is an integer, it represents a 1-based index of the
                 word in `text` to style with the corresponding style.
               - If the value is a string, it matches the word in `text` to style
                 with the corresponding style.
               - If the value is an empty string or `None`, the style will be applied
                 as the final style to all remaining unstyled words in `text`.

        Returns:
           str: The fully styled text, with each word and space styled according to the
           mappings specified in `styles_dict`.
        """
        # Use regular expression to split the text into words and spaces
        words_and_spaces = re.findall(r'\S+|\s+', text)
        styled_tokens = [None] * len(words_and_spaces)
        word_indices = {}
        word_index = 0
        previous_token_index = -1  # Initialize to -1 to start from the beginning

        # First pass: Style words based on styles_dict and record their indices
        for i, token in enumerate(words_and_spaces):
            if not token.isspace():
                word_index += 1  # Increment word index
                applied_style = False
                for style, key in styles_dict.items():
                    if key:  # If key is provided (not empty or None)
                        style_code = self.style_codes.get(style, '')
                        if isinstance(key, int):
                            if key == word_index and style in self.styles:
                                styled_tokens[i] = f"{style_code}{token}{self.reset}"
                                word_indices[i] = style_code
                                previous_token_index = i
                                applied_style = True
                                break
                        else:  # key is a string (word match)
                            if token.strip() == key and style in self.styles:
                                styled_tokens[i] = f"{style_code}{token}{self.reset}"
                                word_indices[i] = style_code
                                previous_token_index = i
                                applied_style = True
                                break
                if not applied_style:
                    styled_tokens[i] = token
                    word_indices[i] = None
            else:
                # Temporarily store spaces; we'll handle them in the next pass
                styled_tokens[i] = token

        # Second pass: Apply styles to words between specified indices or words
        last_style = None
        last_key_index = -1
        for style, key in styles_dict.items():
            if key:  # If key is provided
                style_code = self.style_codes.get(style, '')
                if isinstance(key, int):
                    key_indices = [i for i, idx in enumerate(word_indices.values()) if idx == style_code]
                else:
                    key_indices = [i for i, token in enumerate(words_and_spaces) if token.strip() == key]
                if key_indices:
                    key_index = key_indices[0]
                    # Apply style to tokens between last_key_index and key_index
                    for i in range(last_key_index + 1, key_index):
                        if styled_tokens[i] is None and not words_and_spaces[i].isspace():
                            styled_tokens[i] = f"{style_code}{words_and_spaces[i]}{self.reset}"
                            word_indices[i] = style_code
                    last_key_index = key_index
                    last_style = style_code
            else:
                # Store the last style code for final styling
                last_style = self.style_codes.get(style, '')

        # Apply final style to remaining unstyled words after the last key
        if last_style:
            for i in range(last_key_index + 1, len(words_and_spaces)):
                if styled_tokens[i] is None and not words_and_spaces[i].isspace():
                    styled_tokens[i] = f"{last_style}{words_and_spaces[i]}{self.reset}"
                    word_indices[i] = last_style

        # Third pass: Style spaces based on adjacent words
        for i, token in enumerate(words_and_spaces):
            if token.isspace():
                prev_style = word_indices.get(i - 1)
                next_style = word_indices.get(i + 1)
                if prev_style == next_style and prev_style is not None:
                    # If both adjacent words have the same style, use it
                    styled_tokens[i] = f"{prev_style}{token}{self.reset}"
                elif prev_style is not None:
                    # If only the previous word is styled, use its style
                    styled_tokens[i] = f"{prev_style}{token}{self.reset}"
                elif next_style is not None:
                    # If only the next word is styled, use its style
                    styled_tokens[i] = f"{next_style}{token}{self.reset}"
                else:
                    # Leave space unstyled
                    pass
            else:
                if styled_tokens[i] is None:
                    # Ensure any unstyled tokens are assigned
                    styled_tokens[i] = words_and_spaces[i]

        return ''.join(styled_tokens)

    # Special method called by the print method when style param is a dict
    # Does not style spaces only words
    def _style_words_by_index(self,
                              text: str, style: Dict[Union[int, Tuple[int, int]], str]
                              ) -> str:

        words = text.split()

        for i, word in enumerate(words, start=1):  # Start indexing from 1
            for key in style:
                style_name = style[key]
                style_code = self.style_codes[style_name]
                if isinstance(key, tuple):
                    start, end = key
                    if start <= i <= end and style_name in self.styles:  # Inclusive end
                        words[i - 1] = f"{style_code}{word}{self.reset}"
                elif isinstance(key, int):
                    if key == i and style_name in self.styles:
                        words[i - 1] = f"{style_code}{word}{self.reset}"

        return " ".join(words)

    # Public facing method that accounts for whitespace and styles it and words.
    def style_words_by_index(self, text: str, style: Dict[Union[int, Tuple[int, int]], str]) -> str:
        words_and_spaces = re.findall(r'\S+|\s+', text)
        styled_words_and_spaces = [None] * len(words_and_spaces)
        word_indices = {}
        word_index = 0

        # First pass: style words and record their indices
        for i, token in enumerate(words_and_spaces):
            if not token.isspace():
                word_index += 1
                applied_style = False
                for key in style:
                    style_name = style[key]
                    style_code = self.style_codes.get(style_name, '')
                    if isinstance(key, tuple):
                        start, end = key
                        if start <= word_index <= end and style_name in self.styles:
                            styled_words_and_spaces[i] = f"{style_code}{token}{self.reset}"
                            word_indices[i] = style_code
                            applied_style = True
                            break
                    elif isinstance(key, int):
                        if key == word_index and style_name in self.styles:
                            styled_words_and_spaces[i] = f"{style_code}{token}{self.reset}"
                            word_indices[i] = style_code
                            applied_style = True
                            break
                if not applied_style:
                    styled_words_and_spaces[i] = token
                    word_indices[i] = None
            else:
                # Temporarily store spaces as is; we'll handle them in the next pass
                styled_words_and_spaces[i] = token

        # Second pass: style spaces based on adjacent words
        for i, token in enumerate(words_and_spaces):
            if token.isspace():
                prev_style = word_indices.get(i - 1)
                next_style = word_indices.get(i + 1)
                if prev_style == next_style and prev_style is not None:
                    # If both adjacent words have the same style, use it
                    styled_words_and_spaces[i] = f"{prev_style}{token}{self.reset}"
                elif prev_style is not None:
                    # If only the previous word is styled, use its style
                    styled_words_and_spaces[i] = f"{prev_style}{token}{self.reset}"
                elif next_style is not None:
                    # If only the next word is styled, use its style
                    styled_words_and_spaces[i] = f"{next_style}{token}{self.reset}"
                else:
                    # Leave space unstyled
                    pass

        return ''.join(styled_words_and_spaces)


    @staticmethod
    def contains_ansi_codes(s: str) -> bool:
        return '\033' in s

    @classmethod
    def remove_ansi_codes(cls, text):
        return cls.ansi_escape_pattern.sub('', text)

    @staticmethod
    def write_file(text, filename, end, mode='a'):
        with open(filename, mode) as file:
            file.write(text + end)

    @staticmethod
    def check_dict_structure(d):
        has_tuple_keys = any(isinstance(pkey, tuple) for pkey in d.keys())
        has_int_keys = any(isinstance(pkey, int) for pkey in d.keys())
        has_str_keys = all(isinstance(pkey, str) for pkey in d.keys())

        if has_tuple_keys or has_int_keys:
            # Likely the indexed_style structure
            return "indexed_style"
        elif has_str_keys:
            # Likely the splits structure
            return "splits"
        else:
            return "Unknown structure"


    def format_with_sep(self,
                        *args,
                        converted_args=None,
                        sep=' ',
                        prog_sep='',
                        prog_step=1,
                        start='',
                        prog_direction='forward'
                        ) -> str:

        if not converted_args:
            # Convert args to strings if required
            converted_args = [str(arg) for arg in args] if self.config["args_to_strings"] else args

        self.debug(f"converted_args:\n{converted_args}")

        # Initialize text with the start parameter
        text = ''

        # Handle separator logic
        if isinstance(sep, str):
            if prog_sep:
                # If prog_sep is provided, apply it progressively
                text += converted_args[0]
                for i in range(1, len(converted_args)):
                    # Apply constant separator (now sep) between arguments
                    text += sep
                    if prog_direction == 'reverse':
                        # Apply progressively decreasing separator
                        progressive_sep = prog_sep * ((len(converted_args) - i - 1) * prog_step)
                    else:
                        progressive_sep = prog_sep * (i * prog_step)  # Use step to control progression
                    text += progressive_sep
                    text += converted_args[i]
            else:
                # Standard joining with string separator

                text += sep.join(converted_args)

        elif isinstance(sep, tuple):
            if len(sep) == len(converted_args) - 1:
                # When sep length is one less than number of args, separators go between the args
                text += ''.join(arg + sep[i] for i, arg in enumerate(converted_args[:-1])) + converted_args[-1]
            else:
                raise ValueError(f"Length of sep tuple must be one less than the number of arguments.")
        else:
            raise TypeError(f"sep must be either a string or a tuple, got {type(sep)}")

        final_text = start + text

        return final_text


    @staticmethod
    def get_words_and_spaces(text):
        words = text.split()
        words_and_spaces = []
        index = 0
        for word in words:
            start = text.find(word, index)
            if start > index:
                words_and_spaces.append(text[index:start])
            words_and_spaces.append(word)
            index = start + len(word)
        if index < len(text):
            words_and_spaces.append(text[index:])
        return words_and_spaces




    def print(self,
              *args: Any,
              style: Union[None, str, Dict[Union[int, Tuple[int, int]], str]] = None,
              color: str = None,
              bg_color: str = None,
              reverse: bool = None,
              bold: bool = None,
              dim: bool = None,
              italic: bool = None,
              underline: bool = None,
              overline: bool = None,
              strikethru: bool = None,
              conceal: bool = None,
              blink: bool = None,
              sep: str = ' ',
              prog_sep: str = '',
              prog_step: int = 1,
              prog_direction: str = 'forward',
              share_alike_sep_bg: bool = True,
              share_alike_sep_ul: bool = False,
              share_alike_sep_ol: bool = False,
              share_alike_sep_st: bool = False,
              share_alike_sep_bl: bool = False,
              start: str = '',
              end: str = '\n',
              filename: str = None,
              skip_ansi_check: bool = False,
              phrase_search: bool = True,
              phrase_norm: bool = False,
              phrase_norm_sep: str = ' ',
              word_search: bool = True,
              subword_search: bool = True,
              subword_style_option: int = 1,  # 1, 2, 3, 4, or 5 (see below)
              **kwargs: Any) -> None:



        converted_args = [str(arg) for arg in args] if self.config["args_to_strings"] else args
        self.debug(f'converted_args:\n{converted_args}')

        if not prog_sep:
            text = sep.join(converted_args)
        else:
            text = self.format_with_sep(converted_args=converted_args, sep=sep, prog_sep=prog_sep, prog_step=prog_step, prog_direction=prog_direction)

        self.debug(f"text defined:\n{text}")



        # Handle not colored text
        if not self.config["color_text"]:

            # Remove ANSI codes if present
            if self.contains_ansi_codes(text):
                text = PrintsCharming.remove_ansi_codes(text)

            if filename:
                self.write_file(text, filename, end)
            else:
                print(text, end=end)
            return

        # Check for ANSI codes in converted_args
        if not skip_ansi_check and any(self.contains_ansi_codes(arg) for arg in converted_args):
            if filename:
                self.write_file(text, filename, end)
            else:
                print(text, end=end)
            return


        if isinstance(style, dict):
            dict_type = self.check_dict_structure(style)
            if dict_type == "indexed_style":
                text = self._style_words_by_index(text, style)
            elif dict_type == 'splits':
                text = self.segment_and_style(text, style)
            elif dict_type == 'splits_with_lists':
                text = self.segment_and_style2(text, style)


        if self.config["kwargs"] and kwargs:
            text = self.replace_and_style_placeholders(text, kwargs)

            if filename:
                self.write_file(text, filename, end)
            else:
                print(text, end=end)
            return



        style_instance, style_code = (
            (self.styles.get(style, self.styles['default']), self.style_codes.get(style, self.style_codes['default'])) if style and isinstance(style, str)
            else (self.styles.get('default'), self.style_codes.get('default'))
        )

        if any((color is not None,
                bg_color is not None,
                reverse is not None,
                bold is not None,
                dim is not None,
                italic is not None,
                underline is not None,
                overline is not None,
                strikethru is not None,
                conceal is not None,
                blink is not None)):



            style_instance = copy.copy(style_instance)


            updated_style = {k: v for k, v in {
                'color': color,
                'bg_color': bg_color,
                'reverse': reverse,
                'bold': bold,
                'dim': dim,
                'italic': italic,
                'underline': underline,
                'overline': overline,
                'strikethru': strikethru,
                'conceal': conceal,
                'blink': blink,

            }.items() if v is not None}


            style_instance.update(updated_style)


            style_key = (
                style_instance.color,
                style_instance.bg_color,
                style_instance.reverse,
                style_instance.bold,
                style_instance.dim,
                style_instance.italic,
                style_instance.underline,
                style_instance.overline,
                style_instance.strikethru,
                style_instance.conceal,
                style_instance.blink,
            )

            # Check the cache for the style code
            cached_style_code = self.style_cache.get(style_key)
            if cached_style_code:
                style_code = cached_style_code
            else:
                # Cache the style code
                style_code = self.create_style_code(style_instance)
                self.style_cache[style_key] = style_code


        # Convert the text to a list of words and spaces
        words_and_spaces = self.get_words_and_spaces(text)
        #words_and_spaces = PrintsCharming.words_and_spaces_pattern.findall(text)
        self.debug(f'words_and_spaces:\n{words_and_spaces}')

        # Initialize list to hold the final styled words and spaces
        styled_words_and_spaces = [None] * len(words_and_spaces)


        # Initialize the lists to keep track of which indexes are used by what
        indexes_used_by_phrases = set()
        indexes_used_by_words = set()
        indexes_used_by_substrings = set()
        indexes_used_by_default_styling = set()
        indexes_used_by_spaces = set()
        indexes_used_by_none_styling = set()


        boundary_indices_dict = {}

        # Define sentence-ending characters
        sentence_ending_characters = ".,!?:;"



        # Step 1: Handle phrases
        # Instance level check
        if self.enable_styled_phrases:
            # Method level check
            if phrase_search:
                if len(words_and_spaces) >= self.shortest_phrase_length:
                    for i in range(len(words_and_spaces)):
                        # Build the text segment starting from the current position
                        text_segment = ''.join(words_and_spaces[i:])

                        # Search for the longest matching phrase in the phrase trie
                        phrase_match = self.phrase_trie.search_longest_prefix(text_segment, phrase_norm, phrase_norm_sep)
                        self.debug(f'phrase_match: {phrase_match}')
                        if phrase_match:
                            phrase, details = phrase_match

                            self.debug(f'phrase_match True:\nphrase: {phrase}\n\ndetails: {details}')

                            if not phrase_norm:
                                styled_phrase = details.get('styled', phrase)

                            else:
                                # Get the style code and apply it to the original, unnormalized phrase
                                phrase_style_code = details.get('style_code')
                                styled_phrase = f'{phrase_style_code}{phrase}{self.reset}'

                            self.debug(f'styled_phrase: {styled_phrase}')

                            # Split the styled phrase into words and spaces
                            styled_phrase_words_and_spaces = PrintsCharming.words_and_spaces_pattern.findall(styled_phrase)
                            self.debug(f'styled_phrase_words_and_spaces:\n{styled_phrase_words_and_spaces}')



                            # Ensure the phrase is properly aligned in the words_and_spaces list
                            if words_and_spaces[i:i + len(styled_phrase_words_and_spaces)] == PrintsCharming.words_and_spaces_pattern.findall(phrase):
                                # Update the indexes_used_by_phrases set
                                indexes_used_by_phrases.update(list(range(i, i + len(styled_phrase_words_and_spaces))))
                                self.debug(f'indexes_used_by_phrases:\n{indexes_used_by_phrases}')

                                # Add the index before the starting index
                                if i > 0 and (i - 1) not in boundary_indices_dict:
                                    boundary_indices_dict[i - 1] = details.get('attribs')

                                # Add the index after the ending index
                                if i + len(styled_phrase_words_and_spaces) < len(words_and_spaces) and (i + len(styled_phrase_words_and_spaces)) not in boundary_indices_dict:
                                    boundary_indices_dict[i + len(styled_phrase_words_and_spaces)] = details.get('attribs')

                                # Update the styled_words_and_spaces list with the styled phrase
                                for j, styled_word_or_space in enumerate(styled_phrase_words_and_spaces):
                                    styled_words_and_spaces[i + j] = styled_word_or_space

                                # Move the index forward to skip over the phrase that has just been processed
                                i += len(styled_phrase_words_and_spaces) - 1  # Adjust `i` to the end of the current phrase


        self.debug(f'after phrases:\nindexes_used_by_phrases:\n{indexes_used_by_phrases}\nboundary_indices_dict:\n{boundary_indices_dict}\nstyled_words_and_spaces:\n{styled_words_and_spaces}')


        # Step 2: Handle individual words and substrings
        if self.enable_styled_words:
            if word_search:
                for i, word_or_space in enumerate(words_and_spaces):
                    if i in indexes_used_by_phrases:
                        continue

                    if not word_or_space.isspace():

                        word = word_or_space.strip()  # Strip whitespace around the word
                        self.debug(f'word[{i}]: {word}')
                        stripped_word = word.rstrip(sentence_ending_characters)  # Remove trailing punctuation
                        self.debug(f'stripped_word[{i}]: {stripped_word}')
                        trailing_chars = word[len(stripped_word):]  # Capture any trailing punctuation

                        word_details = None

                        if self.enable_word_trie:
                            # Check if the word is in the word trie
                            word_match = self.word_trie.search_longest_prefix(stripped_word)
                            self.debug(f'word_match: {word_match}')
                            if word_match:
                                matched_word, word_details = word_match
                                self.debug(f'word_match True:\nmatched_word: {matched_word}\nword_details: {word_details}')

                        elif self.enable_word_map:
                            word_details = self.word_map.get(stripped_word)


                        if word_details:
                            self.debug(f'word_details: {word_details}')
                            style_start = word_details.get('style_code', '')
                            self.debug(f'style_start: {style_start}')

                            # Apply the style to the word, accounting for trailing characters
                            if trailing_chars:
                                styled_word_or_space = f'{style_start}{word}{self.reset}'
                            else:
                                styled_word_or_space = word_details.get('styled', stripped_word)

                            self.debug(f'styled_word_or_space: {styled_word_or_space}')

                            # Store the styled word
                            styled_words_and_spaces[i] = styled_word_or_space
                            self.debug(f'styled_words_and_spaces:\n{styled_words_and_spaces}')

                            # Update boundary information
                            if i > 0 and (i - 1) not in boundary_indices_dict:
                                boundary_indices_dict[i - 1] = word_details.get('attribs')

                            if i + 1 < len(words_and_spaces) and (i + 1) not in boundary_indices_dict:
                                boundary_indices_dict[i + 1] = word_details.get('attribs')

                            # Mark the word as styled
                            indexes_used_by_words.add(i)

                        else:
                            if self.enable_styled_subwords and subword_search:
                                if isinstance(subword_style_option, int) and subword_style_option in range(1, 6):
                                    subword_match = False

                                    if subword_style_option == 1:
                                        # Use the specialized prefix search method
                                        prefix_match = self.subword_trie.search_prefix(stripped_word)
                                        if prefix_match:
                                            matched_substring, substring_details = prefix_match
                                            subword_match = True

                                    elif subword_style_option == 2:
                                        # Use the specialized suffix search method
                                        suffix_match = self.subword_trie.search_suffix(stripped_word)
                                        if suffix_match:
                                            matched_substring, substring_details = suffix_match
                                            subword_match = True

                                    elif subword_style_option == 3:
                                        # Earliest added match
                                        substring_matches = self.subword_trie.search_any_substring_by_insertion_order(stripped_word)
                                        if substring_matches:
                                            matched_substring, substring_details, _ = substring_matches[0]
                                            subword_match = True

                                    elif subword_style_option == 4:
                                        # Most recently added match
                                        substring_matches = self.subword_trie.search_any_substring_by_insertion_order(stripped_word)
                                        if substring_matches:
                                            matched_substring, substring_details, _ = substring_matches[-1]
                                            subword_match = True

                                    elif subword_style_option == 5:
                                        # Style only the matching substrings
                                        substring_matches = self.subword_trie.search_any_substring(stripped_word)
                                        if substring_matches:
                                            sorted_matches = sorted(substring_matches, key=lambda match: stripped_word.find(match[0]))
                                            current_position = 0
                                            styled_word_parts = []

                                            for matched_substring, substring_details in sorted_matches:
                                                style_start = substring_details.get('style_code', '')
                                                substring_start = stripped_word.find(matched_substring, current_position)
                                                substring_end = substring_start + len(matched_substring)

                                                # Style the part before the substring
                                                if substring_start > current_position:
                                                    unstyled_part = stripped_word[current_position:substring_start]
                                                    styled_word_parts.append(f"{style_code}{unstyled_part}{self.reset}")

                                                # Apply style to the matched substring
                                                styled_word_parts.append(f"{style_start}{matched_substring}{self.reset}")
                                                current_position = substring_end

                                            # Handle any remaining part after the last substring
                                            if current_position < len(stripped_word):
                                                remaining_part = stripped_word[current_position:]
                                                styled_word_parts.append(f"{style_code}{remaining_part}{self.reset}")

                                            # Combine parts and store the result
                                            styled_word_or_space = ''.join(styled_word_parts)
                                            styled_words_and_spaces[i] = styled_word_or_space

                                            # Update boundary information
                                            if i > 0 and (i - 1) not in boundary_indices_dict:
                                                boundary_indices_dict[i - 1] = sorted_matches[0][1].get('attribs', {})

                                            if i + 1 < len(words_and_spaces) and (i + 1) not in boundary_indices_dict:
                                                boundary_indices_dict[i + 1] = sorted_matches[-1][1].get('attribs', {})

                                            indexes_used_by_substrings.add(i)
                                            continue

                                    if subword_match and subword_style_option != 5:
                                        style_start = substring_details.get('style_code', '')
                                        styled_word_or_space = f'{style_start}{word_or_space}{self.reset}'
                                        styled_words_and_spaces[i] = styled_word_or_space

                                        # Update boundary information
                                        if i > 0 and (i - 1) not in boundary_indices_dict:
                                            boundary_indices_dict[i - 1] = substring_details.get('attribs', {})

                                        if i + 1 < len(words_and_spaces) and (i + 1) not in boundary_indices_dict:
                                            boundary_indices_dict[i + 1] = substring_details.get('attribs', {})

                                        indexes_used_by_substrings.add(i)
                                        continue






        self.debug(f'after words and substrings:\nindexes_used_by_words:\n{indexes_used_by_words}\nindexes_used_by_substrings:\n{indexes_used_by_substrings}\nboundary_indices_dict:\n{boundary_indices_dict}\nstyled_words_and_spaces:\n{styled_words_and_spaces}')
        self.debug(f'styled_words_and_spaces:\n{styled_words_and_spaces}')


        # Step 3: Handle other styled text and spaces
        for i, word_or_space in enumerate(words_and_spaces):
            # Skip the index if it's used by a phrase or a word in the word_map
            if i in indexes_used_by_phrases or i in indexes_used_by_words or i in indexes_used_by_substrings:
                continue

            if word_or_space.isspace():
                indexes_used_by_spaces.add(i)
                if i not in boundary_indices_dict:
                    styled_word_or_space = f"{style_code}{word_or_space}{self.reset}"
                else:

                    style_instance_dict = asdict(style_instance)

                    keys_to_compare = ['color', 'bg_color']
                    if share_alike_sep_ul:
                        keys_to_compare.append('underline')
                    if share_alike_sep_ol:
                        keys_to_compare.append('overline')
                    if share_alike_sep_st:
                        keys_to_compare.append('strikethru')
                    if share_alike_sep_bl:
                        keys_to_compare.append('blink')

                    comparison_results = self.compare_dicts(boundary_indices_dict[i], style_instance_dict, keys_to_compare)


                    space_style_codes = []
                    if share_alike_sep_bg and comparison_results.get('bg_color'):
                        space_style_codes.append(self.bg_color_map.get(style_instance_dict.get('bg_color')))

                    if len(keys_to_compare) > 2:
                        if comparison_results.get('color'):
                            space_style_codes.append(self.color_map.get(style_instance_dict.get('color'), self.color_map.get(boundary_indices_dict[i].get('color', ''))))

                            for key in keys_to_compare[2:]:
                                if comparison_results.get(key):
                                    space_style_codes.append(self.effect_map.get(key, ''))

                    new_style_code = ''.join(space_style_codes)
                    styled_word_or_space = f'{new_style_code}{word_or_space}{self.reset}'


            else:
                indexes_used_by_default_styling.add(i)
                styled_word_or_space = f"{style_code}{word_or_space}{self.reset}"

            # Update the styled_words_and_spaces list
            styled_words_and_spaces[i] = styled_word_or_space

        self.debug(f'After handle other styled text and spaces:\nindexes_used_by_spaces:\n{indexes_used_by_spaces}')
        self.debug(f'styled_words_and_spaces:\n{styled_words_and_spaces}')


        # Step 4: Handle default styling for remaining words and spaces
        for i, styled_word_or_space in enumerate(styled_words_and_spaces):
            if styled_word_or_space is None:
                styled_words_and_spaces[i] = f"{style_code}{words_and_spaces[i]}{self.reset}"
                indexes_used_by_none_styling.add(i)

        self.debug(f'After handle default styling:\nindexes_used_by_none_styling:\n{indexes_used_by_none_styling}')
        self.debug(f'styled_words_and_spaces:\n{styled_words_and_spaces}')


        # Step 5: Join the styled_words_and_spaces to form the final styled text
        styled_text = ''.join(filter(None, styled_words_and_spaces))

        # Step 6: Wrap the final styled text if needed
        wrapped_styled_text = self.formatter.format(styled_text, skip_format=True)

        # Step 7: Add start and end to the final styled text
        if not wrapped_styled_text:
            all_text = start + styled_text + end
        else:
            all_text = start + wrapped_styled_text + end


        # Print or write to file
        if filename:
            with open(filename, 'a') as file:
                file.write(all_text)
        else:
            sys.stdout.write(all_text)
            #print(start + styled_text, end=end)




    def compare_dicts(self, dict1, dict2, keys):
        dict2 = self.apply_reverse_effect(dict2)

        results = {}
        for key in keys:
            if key in ['color', 'bg_color']:
                results[key] = dict1.get(key) == dict2.get(key) and dict1.get(key) is not None
            else:
                results[key] = dict1.get(key) == dict2.get(key) and dict1.get(key) is True
        return results

    @staticmethod
    def apply_reverse_effect(style_dict):
        if style_dict.get('reversed'):
            style_dict['color'], style_dict['bg_color'] = (
                style_dict.get('bg_color'), style_dict.get('color')
            )
        return style_dict


    def print_variables(self, text: str, text_style: str = None, **kwargs) -> None:
        # Apply styles to each variable in kwargs
        for key, value in kwargs.items():
            variable, var_style = value
            styled_var = f"{self.style_codes[var_style]}{str(variable)}{self.reset}"
            kwargs[key] = styled_var

        # Replace placeholders with styled variables
        text = text.format(**kwargs)

        self.print(text, style=text_style, skip_ansi_check=True)


    def replace_and_style_placeholders(self,
                                       text: str,
                                       placeholders: Dict[str, Any],
                                       enable_label_style: bool = True,
                                       top_level_label: str = 'top_level_label',
                                       sub_level_label: str = 'sub_level_label',
                                       label_delimiter: str = ':',
                                       style_function: Callable[[str, Dict[str, Any]], str] = None,
                                       **style_kwargs) -> str:

        """Replace placeholders with actual values and apply colors."""
        self.debug(
            "Replace and style text: {} with placeholders: {}",
            text,
            placeholders
        )
        top_level_label_style_code = self.get_style_code(top_level_label) if enable_label_style else ''
        sub_level_label_style_code = self.get_style_code(sub_level_label) if enable_label_style else ''
        lines = text.split('\n')

        # Style labels directly in the text
        if enable_label_style:
            for i, line in enumerate(lines):
                stripped_line = line.strip()
                # Handle standalone labels that end with ':'
                if stripped_line.endswith(label_delimiter):
                    label, _, rest = line.partition(label_delimiter)
                    lines[i] = f"{sub_level_label_style_code}{label}{label_delimiter}{self.reset}{rest}"
                # Handle inline labels followed by placeholders
                elif label_delimiter in line:
                    label, delimiter, rest = line.partition(label_delimiter)
                    if '{' in rest:
                        lines[i] = f"{top_level_label_style_code}{label}{delimiter}{self.reset}{rest}"

        styled_text = '\n'.join(lines)

        # Replace placeholders with actual values and apply styles
        for key, value in placeholders.items():
            styled_value = str(value)
            if key in self.style_conditions_map:
                style_name = self.style_conditions_map[key](value)
                style_code = self.get_style_code(style_name)
                styled_value = f"{style_code}{styled_value}{self.reset}"
            styled_text = styled_text.replace(f"{{{key}}}", styled_value)

        if not style_function:

            # Apply additional styles for bullets, numbers, and sentences
            lines = styled_text.split('\n')
            for i, line in enumerate(lines):
                stripped_line = line.strip()
                leading_whitespace = line[:len(line) - len(stripped_line)]

                if stripped_line.startswith('- ') and not stripped_line.endswith(':'):
                    # Apply main bullet style
                    parts = stripped_line.split(' ', 1)
                    if len(parts) == 2:
                        lines[
                            i] = f"{leading_whitespace}{self.get_style_code('main_bullets')}{parts[0]} {self.reset}{self.get_style_code('main_bullet_text')}{parts[1]}{self.reset}"
                elif len(stripped_line) > 1 and stripped_line[0].isdigit() and stripped_line[1] == '.':
                    # Apply number and period style, followed by phrase style
                    parts = stripped_line.split('. ', 1)
                    if len(parts) == 2:
                        lines[i] = f"{leading_whitespace}{self.get_style_code('numbers')}{parts[0]}.{self.reset} {self.get_style_code('sub_proj')}{parts[1]}{self.reset}"
                elif stripped_line.startswith('- ') and stripped_line.endswith(':'):
                    # Apply sub-bullet style
                    parts = stripped_line.split(' ', 2)
                    if len(parts) == 3:
                        lines[i] = f"{leading_whitespace}{self.get_style_code('sub_bullets')}{parts[1]} {self.reset}{self.get_style_code('sub_bullet_text')}{parts[2]}{self.reset}"
                elif leading_whitespace.startswith('   '):
                    # Apply sub-bullet sentence style
                    words = stripped_line.split()
                    if len(words) > 1:
                        lines[
                            i] = f"{leading_whitespace}{self.get_style_code('sub_bullet_title')}{words[0]} {self.reset}{self.get_style_code('sub_bullet_sentence')}{' '.join(words[1:])}{self.reset}"

            styled_text = '\n'.join(lines)

        else:
            styled_text = style_function(styled_text, **style_kwargs)

        self.debug(f"Styled text: '{styled_text}'")

        return styled_text


    def print_progress_bar(self, total_steps: int = 4, bar_symbol: str = ' ', bar_length: int = 40, color: str = 'vgreen'):
        for i in range(total_steps):
            progress = (i + 1) / total_steps
            block = int(bar_length * progress)
            if bar_symbol == ' ':
                bar_symbol = self.apply_bg_color(color, bar_symbol)
            bar = bar_symbol * block + "-" * (bar_length - block)
            time.sleep(0.4)
            self.clear_line()
            self.print(f"Progress: |{bar}| {int(progress * 100)}%", end='', color=color)
            sys.stdout.flush()
            time.sleep(0.25)  # Simulate work

    # This is for internal logging within this class!!!
    def setup_internal_logging(self, log_level: str, log_format: str = '%(message)s'):
        """
        Setup logger, configure it with appropriate log level and format.
        """
        # Configure the shared logger's level
        self.logger.setLevel(getattr(logging, log_level.upper(), logging.DEBUG))

        # Logging is controlled by the instance, not by disabling the logger itself
        if self.internal_logging_enabled:
            self.info("Internal Logging Enabled for this instance.")
            logging_enabled_init_message = f"Instance config dict:\n{self.format_dict(self.config)}"
            self.debug(logging_enabled_init_message)



    def _apply_style_internal(self, style_name, text, reset=True):
        # This method does not log debug messages to avoid recursion

        text = str(text)
        if isinstance(text, str) and text.isspace():
            style_code = self.bg_color_map.get(
                style_name,
                self.bg_color_map.get(
                    self.styles.get(style_name, PStyle(bg_color="default_bg")).bg_color
                )
            )
        else:
            style_code = self._internal_logging_style_codes.get(style_name, self.color_map.get(style_name, self.color_map.get('default')))

        # Append the style code at the beginning of the text and the reset code at the end
        styled_text = f"{style_code}{text}{self.reset if reset else ''}"

        return styled_text



    def log(self, level: str, message: str, *args, **kwargs) -> None:
        if not self.config['internal_logging']:
            return

        level = getattr(logging, level, None)

        if args:
            try:
                message = message.format(*args)
            except (IndexError, KeyError, ValueError) as e:
                self.logger.error(f"Error formatting log message: {e}")
                return

        if kwargs:
            message = message.format(**kwargs)

        timestamp = time.time()
        formatted_timestamp = datetime.fromtimestamp(timestamp).strftime(self._TIMESTAMP_FORMAT)

        timestamp_style = 'timestamp'

        level_styles = {
            10: 'debug',
            20: 'info',
            30: 'warning',
            40: 'error',
            50: 'critical',
        }

        log_level_style = level_styles.get(level, 'default')

        styled_log_level_prefix = self._apply_style_internal(log_level_style, f"LOG[{logging.getLevelName(level)}]")
        styled_timestamp = self._apply_style_internal(timestamp_style, formatted_timestamp)
        styled_level = self._apply_style_internal(log_level_style, logging.getLevelName(level))
        styled_text = self._apply_style_internal(log_level_style, message)

        log_message = f"{styled_log_level_prefix} {styled_timestamp} {styled_level} - {styled_text}"
        self.logger.log(level, log_message)


    def debug(self, message: str, *args, **kwargs) -> None:
        # Get the current stack frame
        current_frame = inspect.currentframe()
        # Get the caller frame
        caller_frame = current_frame.f_back
        # Extract the relevant information
        class_name = self._apply_style_internal('class_name', self.__class__.__name__)
        method_name = self._apply_style_internal('method_name', caller_frame.f_code.co_name)
        line_number = self._apply_style_internal('line_number', caller_frame.f_lineno)

        # Include the extracted information in the log message
        message = f"{class_name}.{method_name}:{line_number} - {message}"

        self.log('DEBUG', message, *args, **kwargs)

    def info(self, message: str, *args, **kwargs) -> None:
        self.log('INFO', message, *args, **kwargs)

    def warning(self, message: str, *args, **kwargs) -> None:
        self.log('WARNING', message, *args, **kwargs)

    def error(self, message: str, *args, **kwargs) -> None:
        self.log('ERROR', message, *args, **kwargs)

    def critical(self, message: str, *args, **kwargs) -> None:
        self.log('CRITICAL', message, *args, **kwargs)



    def handle_other_styled_text_and_spaces(self,
                                            words_and_spaces,
                                            styled_words_and_spaces,
                                            indexes_used_by_phrases,
                                            indexes_used_by_words,
                                            indexes_used_by_subwords,
                                            indexes_used_by_spaces,
                                            indexes_used_by_default_styling,
                                            style_instance,
                                            style_code,
                                            share_alike_sep_bg,
                                            share_alike_sep_ul,
                                            share_alike_sep_ol,
                                            share_alike_sep_st,
                                            share_alike_sep_bl,
                                            boundary_indices_dict
                                            ):

        for i, word_or_space in enumerate(words_and_spaces):
            if i in indexes_used_by_phrases or i in indexes_used_by_words or i in indexes_used_by_subwords:
                continue

            if word_or_space.isspace():
                indexes_used_by_spaces.add(i)
                if i not in boundary_indices_dict:
                    styled_word_or_space = f"{style_code}{word_or_space}{self.reset}"
                else:

                    style_instance_dict = asdict(style_instance)

                    keys_to_compare = ['color', 'bg_color']
                    if share_alike_sep_ul:
                        keys_to_compare.append('underline')
                    if share_alike_sep_ol:
                        keys_to_compare.append('overline')
                    if share_alike_sep_st:
                        keys_to_compare.append('strikethru')
                    if share_alike_sep_bl:
                        keys_to_compare.append('blink')

                    comparison_results = self.compare_dicts(boundary_indices_dict[i], style_instance_dict, keys_to_compare)

                    space_style_codes = []
                    if share_alike_sep_bg and comparison_results.get('bg_color'):
                        space_style_codes.append(self.bg_color_map.get(style_instance_dict.get('bg_color')))

                    if len(keys_to_compare) > 2:
                        if comparison_results.get('color'):
                            space_style_codes.append(self.color_map.get(style_instance_dict.get('color'), self.color_map.get(boundary_indices_dict[i].get('color', ''))))

                            for key in keys_to_compare[2:]:
                                if comparison_results.get(key):
                                    space_style_codes.append(self.effect_map.get(key, ''))

                    new_style_code = ''.join(space_style_codes)
                    styled_word_or_space = f'{new_style_code}{word_or_space}{self.reset}'

            else:
                indexes_used_by_default_styling.add(i)
                styled_word_or_space = f"{style_code}{word_or_space}{self.reset}"

            # Update the styled_words_and_spaces list
            styled_words_and_spaces[i] = styled_word_or_space

        return styled_words_and_spaces, indexes_used_by_spaces, indexes_used_by_default_styling



    def handle_words_and_subwords(self,
                                  words_and_spaces,
                                  styled_words_and_spaces,
                                  indexes_used_by_phrases,
                                  indexes_used_by_words,
                                  indexes_used_by_subwords,
                                  subword_search,
                                  subword_style_option,
                                  style_code,
                                  boundary_indices_dict
                                  ):

        sentence_ending_characters = self.sentence_ending_characters

        for i, word_or_space in enumerate(words_and_spaces):
            if i in indexes_used_by_phrases:
                continue

            if not word_or_space.isspace():

                word = word_or_space.strip()
                self.debug(f'word[{i}]: {word}')
                stripped_word = word.rstrip(sentence_ending_characters)
                self.debug(f'stripped_word[{i}]: {stripped_word}')

                # Capture any trailing punctuation
                trailing_chars = word[len(stripped_word):]

                word_details = None

                if self.enable_word_trie:
                    # Check if the word is in the word trie
                    word_match = self.word_trie.search_longest_prefix(stripped_word)
                    self.debug(f'word_match: {word_match}')
                    if word_match:
                        matched_word, word_details = word_match
                        self.debug(f'word_match True:\nmatched_word: {matched_word}\nword_details: {word_details}')

                elif self.enable_word_map:
                    word_details = self.word_map.get(stripped_word)

                if word_details:
                    self.debug(f'word_details: {word_details}')
                    style_start = word_details.get('style_code', '')
                    self.debug(f'style_start: {style_start}')

                    # Apply the style to the word, accounting for trailing characters
                    if trailing_chars:
                        styled_word_or_space = f'{style_start}{word}{self.reset}'
                    else:
                        styled_word_or_space = word_details.get('styled', stripped_word)

                    self.debug(f'styled_word_or_space: {styled_word_or_space}')

                    # Store the styled word
                    styled_words_and_spaces[i] = styled_word_or_space
                    self.debug(f'styled_words_and_spaces:\n{styled_words_and_spaces}')

                    # Update boundary information
                    if i > 0 and (i - 1) not in boundary_indices_dict:
                        boundary_indices_dict[i - 1] = word_details.get('attribs')

                    if i + 1 < len(words_and_spaces) and (i + 1) not in boundary_indices_dict:
                        boundary_indices_dict[i + 1] = word_details.get('attribs')

                    # Mark the word as styled
                    indexes_used_by_words.add(i)

                else:
                    if self.enable_styled_subwords and subword_search:
                        if isinstance(subword_style_option, int) and subword_style_option in range(1, 6):
                            subword_match = False

                            if subword_style_option == 1:
                                # Use the specialized prefix search method
                                prefix_match = self.subword_trie.search_prefix(stripped_word)
                                if prefix_match:
                                    matched_substring, substring_details = prefix_match
                                    subword_match = True

                            elif subword_style_option == 2:
                                # Use the specialized suffix search method
                                suffix_match = self.subword_trie.search_suffix(stripped_word)
                                if suffix_match:
                                    matched_substring, substring_details = suffix_match
                                    subword_match = True

                            elif subword_style_option == 3:
                                # Earliest added match
                                substring_matches = self.subword_trie.search_any_substring_by_insertion_order(stripped_word)
                                if substring_matches:
                                    matched_substring, substring_details, _ = substring_matches[0]
                                    subword_match = True

                            elif subword_style_option == 4:
                                # Most recently added match
                                substring_matches = self.subword_trie.search_any_substring_by_insertion_order(stripped_word)
                                if substring_matches:
                                    matched_substring, substring_details, _ = substring_matches[-1]
                                    subword_match = True

                            elif subword_style_option == 5:
                                # Style only the matching substrings
                                substring_matches = self.subword_trie.search_any_substring(stripped_word)
                                if substring_matches:
                                    sorted_matches = sorted(substring_matches, key=lambda match: stripped_word.find(match[0]))
                                    current_position = 0
                                    styled_word_parts = []

                                    for matched_substring, substring_details in sorted_matches:
                                        style_start = substring_details.get('style_code', '')
                                        substring_start = stripped_word.find(matched_substring, current_position)
                                        substring_end = substring_start + len(matched_substring)

                                        # Style the part before the substring
                                        if substring_start > current_position:
                                            unstyled_part = stripped_word[current_position:substring_start]
                                            styled_word_parts.append(f"{style_code}{unstyled_part}{self.reset}")

                                        # Apply style to the matched substring
                                        styled_word_parts.append(f"{style_start}{matched_substring}{self.reset}")
                                        current_position = substring_end

                                    # Handle any remaining part after the last substring
                                    if current_position < len(stripped_word):
                                        remaining_part = stripped_word[current_position:]
                                        styled_word_parts.append(f"{style_code}{remaining_part}{self.reset}")

                                    # Combine parts and store the result
                                    styled_word_or_space = ''.join(styled_word_parts)
                                    styled_words_and_spaces[i] = styled_word_or_space

                                    # Update boundary information
                                    if i > 0 and (i - 1) not in boundary_indices_dict:
                                        boundary_indices_dict[i - 1] = sorted_matches[0][1].get('attribs', {})

                                    if i + 1 < len(words_and_spaces) and (i + 1) not in boundary_indices_dict:
                                        boundary_indices_dict[i + 1] = sorted_matches[-1][1].get('attribs', {})

                                    indexes_used_by_subwords.add(i)
                                    continue

                            if subword_match and subword_style_option != 5:
                                style_start = substring_details.get('style_code', '')
                                styled_word_or_space = f'{style_start}{word_or_space}{self.reset}'
                                styled_words_and_spaces[i] = styled_word_or_space

                                # Update boundary information
                                if i > 0 and (i - 1) not in boundary_indices_dict:
                                    boundary_indices_dict[i - 1] = substring_details.get('attribs', {})

                                if i + 1 < len(words_and_spaces) and (i + 1) not in boundary_indices_dict:
                                    boundary_indices_dict[i + 1] = substring_details.get('attribs', {})

                                indexes_used_by_subwords.add(i)
                                continue

        return styled_words_and_spaces, indexes_used_by_words, indexes_used_by_subwords, boundary_indices_dict


    def handle_phrases(self,
                       words_and_spaces,
                       styled_words_and_spaces,
                       indexes_used_by_phrases,
                       phrase_norm,
                       phrase_norm_sep,
                       boundary_indices_dict):

        for i in range(len(words_and_spaces)):
            # Build the text segment starting from the current position
            text_segment = ''.join(words_and_spaces[i:])

            # Search for the longest matching phrase in the phrase trie
            phrase_match = self.phrase_trie.search_longest_prefix(text_segment, phrase_norm, phrase_norm_sep)
            self.debug(f'phrase_match: {phrase_match}')

            if phrase_match:
                phrase, details = phrase_match
                self.debug(f'phrase_match True:\nphrase: {phrase}\n\ndetails: {details}')

                if not phrase_norm:
                    styled_phrase = details.get('styled', phrase)

                else:
                    # Get the style code and apply it to the original, unnormalized phrase
                    phrase_style_code = details.get('style_code')
                    styled_phrase = f'{phrase_style_code}{phrase}{self.reset}'

                self.debug(f'styled_phrase: {styled_phrase}')

                # Split the styled phrase into words and spaces
                styled_phrase_words_and_spaces = PrintsCharming.words_and_spaces_pattern.findall(styled_phrase)
                styled_phrase_len = len(styled_phrase_words_and_spaces)

                self.debug(f'styled_phrase_length: {styled_phrase_len}')
                self.debug(f'styled_phrase_words_and_spaces:\n{styled_phrase_words_and_spaces}')

                # Ensure the phrase is properly aligned in the words_and_spaces list
                if words_and_spaces[i:i + styled_phrase_len] == PrintsCharming.words_and_spaces_pattern.findall(phrase):
                    # Update the indexes_used_by_phrases set
                    indexes_used_by_phrases.update(list(range(i, i + styled_phrase_len)))
                    self.debug(f'indexes_used_by_phrases:\n{indexes_used_by_phrases}')

                    # Add the index before the starting index
                    if i > 0 and (i - 1) not in boundary_indices_dict:
                        boundary_indices_dict[i - 1] = details.get('attribs')

                    # Add the index after the ending index
                    if i + styled_phrase_len < len(words_and_spaces) and (i + styled_phrase_len) not in boundary_indices_dict:
                        boundary_indices_dict[i + styled_phrase_len] = details.get('attribs')

                    # Update the styled_words_and_spaces list with the styled phrase
                    for j, styled_word_or_space in enumerate(styled_phrase_words_and_spaces):
                        styled_words_and_spaces[i + j] = styled_word_or_space

                    # Move the index forward to skip over the phrase that has just been processed
                    i += styled_phrase_len - 1  # Adjust `i` to the end of the current phrase

        return styled_words_and_spaces, indexes_used_by_phrases, boundary_indices_dict


    def get_style_instance_and_code(self,
                                    style,
                                    color,
                                    bg_color,
                                    reverse,
                                    bold,
                                    dim,
                                    italic,
                                    underline,
                                    overline,
                                    strikethru,
                                    conceal,
                                    blink
                                    ):

        style_instance, style_code = (
            (self.styles.get(style, self.styles['default']), self.style_codes.get(style, self.style_codes['default'])) if style and isinstance(style, str)
            else (self.styles.get('default'), self.style_codes.get('default'))
        )

        if any((color is not None,
                bg_color is not None,
                reverse is not None,
                bold is not None,
                dim is not None,
                italic is not None,
                underline is not None,
                overline is not None,
                strikethru is not None,
                conceal is not None,
                blink is not None)):

            style_instance = copy.copy(style_instance)

            updated_style = {k: v for k, v in {
                'color': color,
                'bg_color': bg_color,
                'reverse': reverse,
                'bold': bold,
                'dim': dim,
                'italic': italic,
                'underline': underline,
                'overline': overline,
                'strikethru': strikethru,
                'conceal': conceal,
                'blink': blink,

            }.items() if v is not None}

            style_instance.update(updated_style)

            style_key = (
                style_instance.color,
                style_instance.bg_color,
                style_instance.reverse,
                style_instance.bold,
                style_instance.dim,
                style_instance.italic,
                style_instance.underline,
                style_instance.overline,
                style_instance.strikethru,
                style_instance.conceal,
                style_instance.blink,
            )

            # Check the cache for the style code
            cached_style_code = self.style_cache.get(style_key)
            if cached_style_code:
                style_code = cached_style_code
            else:
                # Cache the style code
                style_code = self.create_style_code(style_instance)
                self.style_cache[style_key] = style_code

        return style_instance, style_code


    def print2(self,
               *args: Any,
               style: Union[None, str, Dict[Union[int, Tuple[int, int]], str], List[Union[None, str, Dict[Union[int, Tuple[int, int]], str]]]] = None,
               color: Union[None, str, List[Union[None, str]]] = None,
               bg_color: Union[None, str, List[Union[None, str]]] = None,
               reverse: Union[None, bool, List[Union[None, bool]]] = None,
               bold: Union[None, bool, List[Union[None, bool]]] = None,
               dim: Union[None, bool, List[Union[None, bool]]] = None,
               italic: Union[None, bool, List[Union[None, bool]]] = None,
               underline: Union[None, bool, List[Union[None, bool]]] = None,
               overline: Union[None, bool, List[Union[None, bool]]] = None,
               strikethru: Union[None, bool, List[Union[None, bool]]] = None,
               conceal: Union[None, bool, List[Union[None, bool]]] = None,
               blink: Union[None, bool, List[Union[None, bool]]] = None,
               sep: str = ' ',
               prog_sep: str = '',
               prog_step: int = 1,
               prog_direction: str = 'forward',
               share_alike_sep_bg: bool = True,
               share_alike_sep_ul: bool = False,
               share_alike_sep_ol: bool = False,
               share_alike_sep_st: bool = False,
               share_alike_sep_bl: bool = False,
               start: str = '',
               end: str = '\n',
               filename: str = None,
               skip_ansi_check: bool = False,
               phrase_search: bool = True,
               phrase_norm: bool = False,
               phrase_norm_sep: str = ' ',
               word_search: bool = True,
               subword_search: bool = True,
               subword_style_option: int = 1,  # 1, 2, 3, 4, or 5 (see below)
               style_args_as_one: bool = True,
               return_styled_args_list: bool = False,
               **kwargs: Any
               ) -> Union[None, List[str]]:



        converted_args = [str(arg) for arg in args]
        self.debug(f'converted_args:\n{converted_args}')

        if not self.config["color_text"]:
            # Remove ANSI codes if present
            if any(self.contains_ansi_codes(arg) for arg in converted_args):
                converted_args = [PrintsCharming.remove_ansi_codes(arg) for arg in converted_args]

            text = sep.join(converted_args)  # Join args into final text

            text = start + text

            if filename:
                self.write_file(text, filename, end)
            else:
                print(text, end=end)
            return


        # Check for ANSI codes in converted_args if skip_ansi_check is False
        if not skip_ansi_check and any(self.contains_ansi_codes(arg) for arg in converted_args):
            text = sep.join(converted_args)
            text = start + text
            if filename:
                self.write_file(text, filename, end)
            else:
                print(text, end=end)
            return



        if style_args_as_one:
            style_instance, style_code = self.get_style_instance_and_code(style,
                                                                          color,
                                                                          bg_color,
                                                                          reverse,
                                                                          bold,
                                                                          dim,
                                                                          italic,
                                                                          underline,
                                                                          overline,
                                                                          strikethru,
                                                                          conceal,
                                                                          blink)

            if not prog_sep:
                text = sep.join(converted_args)
            else:
                text = self.format_with_sep(converted_args=converted_args, sep=sep, prog_sep=prog_sep, prog_step=prog_step, prog_direction=prog_direction)

            self.debug(f"text defined:\n{text}")


            if isinstance(style, dict):
                dict_type = self.check_dict_structure(style)
                if dict_type == "indexed_style":
                    text = self._style_words_by_index(text, style)
                elif dict_type == 'splits':
                    text = self.segment_and_style(text, style)
                elif dict_type == 'splits_with_lists':
                    text = self.segment_and_style2(text, style)


            if self.config["kwargs"] and kwargs:
                text = self.replace_and_style_placeholders(text, kwargs)

                if filename:
                    self.write_file(text, filename, end)
                else:
                    print(text, end=end)
                return

            # Convert the text to a list of words and spaces
            words_and_spaces = PrintsCharming.words_and_spaces_pattern.findall(text)
            words_and_spaces_length = len(words_and_spaces)
            self.debug(f'words_and_spaces:\n{words_and_spaces}')

            # Initialize list to hold the final styled words and spaces
            styled_words_and_spaces = [None] * words_and_spaces_length

            # Initialize the lists to keep track of which indexes are used by what
            indexes_used_by_phrases = set()
            indexes_used_by_words = set()
            indexes_used_by_subwords = set()
            indexes_used_by_default_styling = set()
            indexes_used_by_spaces = set()
            indexes_used_by_none_styling = set()

            boundary_indices_dict = {}

            # Step 1: Handle phrases
            # Instance level check
            if self.enable_styled_phrases:
                # Method level check
                if phrase_search:
                    # Only perform phrase lookup if there are multiple elements (implying a possible phrase)
                    if words_and_spaces_length > 1:
                        self.debug(f'Calling self.handle_phrases()')

                        (styled_words_and_spaces,
                         indexes_used_by_phrases,
                         boundary_indices_dict) = self.handle_phrases(words_and_spaces,
                                                                      styled_words_and_spaces,
                                                                      indexes_used_by_phrases,
                                                                      phrase_norm,
                                                                      phrase_norm_sep,
                                                                      boundary_indices_dict)

                        self.debug(f'self.handle_phrases() returned')

            self.debug(f'After Step 1:\nstyled_words_and_spaces:\n{styled_words_and_spaces}\nindexes_used_by_phrases:\n{indexes_used_by_phrases}\nboundary_indices_dict:\n{boundary_indices_dict}\n')

            # Step 2: Handle individual words and substrings
            if self.enable_styled_words:
                if word_search:
                    self.debug(f'Calling self.handle_words_and_subwords()')

                    (styled_words_and_spaces,
                     indexes_used_by_words,
                     indexes_used_by_subwords,
                     boundary_indices_dict) = self.handle_words_and_subwords(words_and_spaces,
                                                                             styled_words_and_spaces,
                                                                             indexes_used_by_phrases,
                                                                             indexes_used_by_words,
                                                                             indexes_used_by_subwords,
                                                                             subword_search,
                                                                             subword_style_option,
                                                                             style_code,
                                                                             boundary_indices_dict)

                    self.debug(f'self.handle_words_and_subwords() returned')


            self.debug(f'After Step 2:\nstyled_words_and_spaces:\n{styled_words_and_spaces}\nindexes_used_by_words:\n{indexes_used_by_words}\nindexes_used_by_subwords:\n{indexes_used_by_subwords}\nboundary_indices_dict:\n{boundary_indices_dict}\n')

            # Step 3: Handle other styled text and spaces
            self.debug(f'Calling self.handle_other_styled_text_and_spaces()')

            (styled_words_and_spaces,
             indexes_used_by_spaces,
             indexes_used_by_default_styling) = self.handle_other_styled_text_and_spaces(words_and_spaces,
                                                                                         styled_words_and_spaces,
                                                                                         indexes_used_by_phrases,
                                                                                         indexes_used_by_words,
                                                                                         indexes_used_by_subwords,
                                                                                         indexes_used_by_spaces,
                                                                                         indexes_used_by_default_styling,
                                                                                         style_instance,
                                                                                         style_code,
                                                                                         share_alike_sep_bg,
                                                                                         share_alike_sep_ul,
                                                                                         share_alike_sep_ol,
                                                                                         share_alike_sep_st,
                                                                                         share_alike_sep_bl,
                                                                                         boundary_indices_dict)

            self.debug(f'self.handle_other_styled_text_and_spaces() returned')


            self.debug(f'After Step 3:\nstyled_words_and_spaces:\n{styled_words_and_spaces}\nindexes_used_by_spaces:\n{indexes_used_by_spaces}\nindexes_used_by_default_styling:\n{indexes_used_by_default_styling}\n')

            # Step 4: Handle default styling for remaining words and spaces
            self.debug(f'Handling default styling for remaining words and spaces.')

            for i, styled_word_or_space in enumerate(styled_words_and_spaces):
                if styled_word_or_space is None:
                    styled_words_and_spaces[i] = f"{style_code}{words_and_spaces[i]}{self.reset}"
                    indexes_used_by_none_styling.add(i)

            self.debug(f'After handle default styling:\nindexes_used_by_none_styling:\n{indexes_used_by_none_styling}')
            self.debug(f'styled_words_and_spaces:\n{styled_words_and_spaces}')

            # Step 5: Join the styled_words_and_spaces to form the final styled text
            styled_text = ''.join(filter(None, styled_words_and_spaces))

            # Print or write to file
            if filename:
                with open(filename, 'a') as file:
                    file.write(start + styled_text + end)
            else:
                sys.stdout.write(start + styled_text + end)
                # print(start + styled_text, end=end)

        else:

            # Ensure all parameters are lists to handle individual styling for each arg
            def ensure_list(param, length):
                if param is None or isinstance(param, str) or isinstance(param, bool) or isinstance(param, dict):
                    return [param] * length  # Broadcast single value to all args
                return param

            num_args = len(converted_args)
            styles = ensure_list(style, num_args)
            colors = ensure_list(color, num_args)
            bg_colors = ensure_list(bg_color, num_args)
            reverses = ensure_list(reverse, num_args)
            bolds = ensure_list(bold, num_args)
            dims = ensure_list(dim, num_args)
            italics = ensure_list(italic, num_args)
            underlines = ensure_list(underline, num_args)
            overlines = ensure_list(overline, num_args)
            strikethrus = ensure_list(strikethru, num_args)
            conceals = ensure_list(conceal, num_args)
            blinks = ensure_list(blink, num_args)

            # Handle kwargs replacements
            if self.config["kwargs"] and kwargs:
                converted_args = [self.replace_and_style_placeholders(arg, kwargs) for arg in converted_args]

            styled_parts = []

            for i, arg in enumerate(converted_args):
                # Apply the corresponding style for the i-th argument
                style_instance, style_code = self.get_style_instance_and_code(styles[i],
                                                                              colors[i],
                                                                              bg_colors[i],
                                                                              reverses[i],
                                                                              bolds[i],
                                                                              dims[i],
                                                                              italics[i],
                                                                              underlines[i],
                                                                              overlines[i],
                                                                              strikethrus[i],
                                                                              conceals[i],
                                                                              blinks[i])

                if isinstance(styles[i], dict):
                    dict_type = self.check_dict_structure(styles[i])
                    if dict_type == "indexed_style":
                        arg = self._style_words_by_index(arg, styles[i])
                    elif dict_type == 'splits':
                        arg = self.segment_and_style(arg, styles[i])
                    elif dict_type == 'splits_with_lists':
                        arg = self.segment_and_style2(arg, styles[i])


                #if isinstance(styles[i], dict):
                    #arg = self._style_words_by_index(arg, styles[i])



                # Convert the text to a list of words and spaces
                words_and_spaces = PrintsCharming.words_and_spaces_pattern.findall(arg)
                words_and_spaces_length = len(words_and_spaces)
                self.debug(f'words_and_spaces:\n{words_and_spaces}')

                # Initialize list to hold the final styled words and spaces
                styled_words_and_spaces = [None] * words_and_spaces_length

                # Initialize the lists to keep track of which indexes are used by what
                indexes_used_by_phrases = set()
                indexes_used_by_words = set()
                indexes_used_by_subwords = set()
                indexes_used_by_default_styling = set()
                indexes_used_by_spaces = set()
                indexes_used_by_none_styling = set()

                boundary_indices_dict = {}


                # Step 1: Handle phrases
                # Instance level check
                if self.enable_styled_phrases:
                    # Method level check
                    if phrase_search:
                        if len(words_and_spaces) >= self.shortest_phrase_length:
                            self.debug(f'Calling self.handle_phrases()')

                            (styled_words_and_spaces,
                             indexes_used_by_phrases,
                             boundary_indices_dict) = self.handle_phrases(words_and_spaces,
                                                                          styled_words_and_spaces,
                                                                          indexes_used_by_phrases,
                                                                          phrase_norm,
                                                                          phrase_norm_sep,
                                                                          boundary_indices_dict)

                            self.debug(f'self.handle_phrases() returned')

                self.debug(
                    f'after phrases:\nindexes_used_by_phrases:\n{indexes_used_by_phrases}\nboundary_indices_dict:\n{boundary_indices_dict}\nstyled_words_and_spaces:\n{styled_words_and_spaces}')

                # Step 2: Handle individual words and substrings
                if self.enable_styled_words:
                    if word_search:
                        self.debug(f'Calling self.handle_words_and_subwords()')

                        (styled_words_and_spaces,
                         indexes_used_by_words,
                         indexes_used_by_subwords,
                         boundary_indices_dict) = self.handle_words_and_subwords(words_and_spaces,
                                                                                 styled_words_and_spaces,
                                                                                 indexes_used_by_phrases,
                                                                                 indexes_used_by_words,
                                                                                 indexes_used_by_subwords,
                                                                                 subword_search,
                                                                                 subword_style_option,
                                                                                 style_code,
                                                                                 boundary_indices_dict)

                        self.debug(f'self.handle_words_and_subwords() returned')

                self.debug(
                    f'after words and subwords:\nindexes_used_by_words:\n{indexes_used_by_words}\nindexes_used_by_subwords:\n{indexes_used_by_subwords}\nboundary_indices_dict:\n{boundary_indices_dict}\nstyled_words_and_spaces:\n{styled_words_and_spaces}')
                self.debug(f'styled_words_and_spaces:\n{styled_words_and_spaces}')

                # Step 3: Handle other styled text and spaces
                self.debug(f'Calling self.handle_other_styled_text_and_spaces()')

                (styled_words_and_spaces,
                 indexes_used_by_spaces,
                 indexes_used_by_default_styling) = self.handle_other_styled_text_and_spaces(words_and_spaces,
                                                                                             styled_words_and_spaces,
                                                                                             indexes_used_by_phrases,
                                                                                             indexes_used_by_words,
                                                                                             indexes_used_by_subwords,
                                                                                             indexes_used_by_spaces,
                                                                                             indexes_used_by_default_styling,
                                                                                             style_instance,
                                                                                             style_code,
                                                                                             share_alike_sep_bg,
                                                                                             share_alike_sep_ul,
                                                                                             share_alike_sep_ol,
                                                                                             share_alike_sep_st,
                                                                                             share_alike_sep_bl,
                                                                                             boundary_indices_dict)

                self.debug(f'self.handle_other_styled_text_and_spaces() returned')

                self.debug(f'After Step 3:\nstyled_words_and_spaces:\n{styled_words_and_spaces}\nindexes_used_by_spaces:\n{indexes_used_by_spaces}\nindexes_used_by_default_styling:\n{indexes_used_by_default_styling}\n')

                # Step 4: Handle default styling for remaining words and spaces
                for j, styled_word_or_space in enumerate(styled_words_and_spaces):
                    if styled_word_or_space is None:
                        styled_words_and_spaces[j] = f"{style_code}{words_and_spaces[j]}{self.reset}"
                        indexes_used_by_none_styling.add(j)

                self.debug(f'After handle default styling:\nindexes_used_by_none_styling:\n{indexes_used_by_none_styling}')
                self.debug(f'styled_words_and_spaces:\n{styled_words_and_spaces}')

                # Step 5: Join the styled_words_and_spaces to form the final styled text
                styled_text = ''.join(filter(None, styled_words_and_spaces))

                # Step 6: Append styled_text to styled_parts list
                styled_parts.append(styled_text)

                #styled_arg = f"{style_code}{arg}{self.reset}"
                #styled_parts.append(styled_arg)

            if return_styled_args_list:
                return styled_parts


            if not prog_sep:
                styled_parts_with_sep = sep.join(styled_parts)
            else:
                styled_parts_with_sep = self.format_with_sep(converted_args=styled_parts, sep=sep, prog_sep=prog_sep, prog_step=prog_step, prog_direction=prog_direction)



            # Print or write to file
            if filename:
                with open(filename, 'a') as file:
                    file.write(start + styled_parts_with_sep + end)
            else:
                sys.stdout.write(start + styled_parts_with_sep + end)
                # print(start + styled_text, end=end)




    def apply_custom_python_highlighting(self, code_block):
        reset_code = PrintsCharming.RESET

        # Pattern to match ANSI escape sequences (like 38;5;248m) and exclude them from further styling
        ansi_escape_sequence_pattern = r'\033\[[0-9;]*m'

        # Simple regex patterns for Python elements
        builtin_pattern = r'\b(print|input|len|range|map|filter|open|help)\b'
        keyword_pattern = r'\b(def|return|print|class|if|else|elif|for|while|import|from|as|in|try|except|finally|not|and|or|is|with|lambda|yield)\b'
        string_pattern = r'(\".*?\"|\'.*?\')'
        comment_pattern = r'(#.*?$)'
        variable_pattern = r'(\b\w+)\s*(=)'  # Capture variables being assigned and preserve spaces
        fstring_pattern = r'\{(\w+)\}'
        number_pattern = r'(?<!\033\[|\d;)\b\d+(\.\d+)?\b'  # Exclude sequences like 5 in "38;5;248m"

        # Pattern for matching function signatures
        function_pattern = r'(\b\w+)(\()([^\)]*)(\))(\s*:)'
        function_call_pattern = r'(\b\w+)(\()([^\)]*)(\))'  # Function calls without a trailing colon
        #param_pattern = r'(\w+)(\s*=\s*)(\w+)?'  # For parameters with default values
        param_pattern = r'(\w+)(\s*=\s*)([^\),]+)'  # This pattern captures the parameters and their default values
        cls_param_pattern = r'\bcls\b'   # For detecting 'cls' parameter
        self_param_pattern = r'\bself\b'  # For detecting 'self' parameter

        # Exclude ANSI escape sequences from number styling
        code_block = re.sub(ansi_escape_sequence_pattern, lambda match: match.group(0), code_block)

        # Apply styles to comments, strings, builtins, keywords
        code_block = re.sub(comment_pattern, f'{self.style_codes.get('python_comment', '')}\\g<0>{reset_code}', code_block, flags=re.MULTILINE)
        code_block = re.sub(string_pattern, f'{self.style_codes.get('python_string', '')}\\g<0>{reset_code}', code_block)
        code_block = re.sub(builtin_pattern, f'{self.style_codes.get('python_builtin', '')}\\g<0>{reset_code}', code_block)
        code_block = re.sub(keyword_pattern, f'{self.style_codes.get('python_keyword', '')}\\g<0>{reset_code}', code_block)

        # Now apply number styling to numbers that are not part of ANSI sequences
        code_block = re.sub(number_pattern, f'{self.style_codes.get('python_number', '')}\\g<0>{reset_code}', code_block)

        # Apply styles to variables
        code_block = re.sub(variable_pattern, f'{self.style_codes.get('python_variable', '')}\\1{reset_code} \\2', code_block)

        # Apply f-string variable styling inside curly braces
        code_block = re.sub(fstring_pattern, f'{self.style_codes.get('python_fstring_variable', '')}{{\\1}}{reset_code}', code_block)

        # Function to style parameters
        def param_replacer(param_match):
            param_name = re.sub(ansi_escape_sequence_pattern, '', param_match.group(1))  # Exclude ANSI sequences
            equal_sign = param_match.group(2).strip()
            default_value = param_match.group(3)

            styled_param_name = f'{self.style_codes["python_param"]}{param_name}{reset_code}'
            styled_equal_sign = f'{self.style_codes["python_operator"]}{equal_sign}{reset_code}'
            styled_default_value = f'{self.style_codes["python_default_value"]}{default_value}{reset_code}'
            params = f'{styled_param_name}{styled_equal_sign}{styled_default_value}'

            return params

        # Match function signatures and apply styles to different parts
        def function_replacer(match):
            function_name = re.sub(ansi_escape_sequence_pattern, '', match.group(1))  # Function name
            parenthesis_open = re.sub(ansi_escape_sequence_pattern, '', match.group(2))
            params = re.sub(ansi_escape_sequence_pattern, '', match.group(3))  # Parameters
            parenthesis_close = re.sub(ansi_escape_sequence_pattern, '', match.group(4))
            colon = match.group(5) if len(match.groups()) == 5 else ''

            # Apply styles and reset codes
            styled_function_name = f'{self.style_codes["python_function_name"]}{function_name}{reset_code}'
            styled_parenthesis_open = f'{self.style_codes["python_parenthesis"]}{parenthesis_open}{reset_code}'
            styled_params = re.sub(cls_param_pattern, f'{self.style_codes["python_self_param"]}cls{reset_code}', params)
            styled_params = re.sub(self_param_pattern, f'{self.style_codes["python_self_param"]}self{reset_code}', styled_params)
            styled_params = re.sub(param_pattern, param_replacer, styled_params)
            styled_parenthesis_close = f'{self.style_codes["python_parenthesis"]}{parenthesis_close}{reset_code}'
            styled_colon = f'{self.style_codes["python_colon"]}{colon}{reset_code}'

            function_sig = f'{styled_function_name}{styled_parenthesis_open}{styled_params}{styled_parenthesis_close}{styled_colon}'

            self.debug(f'{function_sig}')

            return function_sig


        # Apply the function_replacer for function signatures
        code_block = re.sub(function_pattern, function_replacer, code_block)
        self.debug(f'\n\n{code_block}\n')

        # Match and style function calls (function calls don't have trailing colons)
        def function_call_replacer(match):
            #function_name = f'{function_name_style_code}{match.group(1)}{reset_code}'  # Function name in calls
            function_name = re.sub(ansi_escape_sequence_pattern, '', match.group(1))  # Function name
            #parenthesis_open = f'{parenthesis_style_code}{match.group(2)}{reset_code}'
            parenthesis_open = re.sub(ansi_escape_sequence_pattern, '', match.group(2))
            #params = match.group(3)
            params = re.sub(ansi_escape_sequence_pattern, '', match.group(3))  # Exclude ANSI sequences
            #parenthesis_close = f'{parenthesis_style_code}{match.group(4)}{reset_code}'
            parenthesis_close = re.sub(ansi_escape_sequence_pattern, '', match.group(4))

            # Apply styles to 'cls' parameter within function calls
            styled_params = re.sub(cls_param_pattern, f'{self.style_codes.get('python_self_param', '')}cls{reset_code}', params)

            # Apply styles to 'self' parameter within function calls
            styled_params = re.sub(self_param_pattern, f'{self.style_codes.get('python_self_param', '')}self{reset_code}', params)

            # Apply styles to parameters with default values
            styled_params = re.sub(param_pattern, param_replacer, styled_params)

            styled_function_call = f'{function_name}{parenthesis_open}{styled_params}{parenthesis_close}'

            return styled_function_call

        # Apply the function_call_replacer for function calls
        code_block = re.sub(function_call_pattern, function_call_replacer, code_block)
        self.debug(f'\n\n{code_block}\n')

        return code_block


    def apply_markdown_style(self, style_name, text, nested_styles=None, reset=True):
        text = str(text)

        # Handle nested styles first, if provided
        if nested_styles:
            for nested_style in nested_styles:
                text = self.apply_markdown_style(nested_style, text, reset=False)

        # Fetch the corresponding style code
        style_code = self.style_codes.get(style_name, self.color_map.get(style_name, self.color_map.get('default')))

        # Apply reset code carefully for nested styles
        reset_code = self.reset if reset else ''

        # Handle code block separately for better readability
        if style_name == 'code_block':
            # styled_text = f"{style_code}\n{text}\n{reset_code}"  # Add extra line breaks for code blocks
            language = text.split("\n", 1)[0]  # Get the first line, which is the language identifier (e.g., 'python')
            code = text[len(language):]  # The rest is the actual code block content
            highlighted_code = self.apply_custom_python_highlighting(code.strip())
            # Combine the language identifier with the highlighted code block
            styled_text = f"\n\n{style_code}{language}{reset_code}\n\n{highlighted_code}"
        else:
            # Apply the style and reset code for other markdown types
            styled_text = f"{style_code}{text}{reset_code}"

        return styled_text



    def parse_markdown(self, text: str) -> List[Tuple[str, str]]:
        parsed_segments = []

        # Match everything in the correct order, including code blocks
        pattern = re.compile(r"```(\w*)\n([\s\S]*?)```|^(#+)\s+(.+)|\*\*(.+?)\*\*|\*(.+?)\*|-\s+(.+)|\[(.+?)\]\((.+?)\)|`([^`]+)`", re.MULTILINE)

        for match in pattern.finditer(text):
            if match.group(1) is not None:  # Code block
                language = match.group(1) or 'plain'
                code_block = match.group(2).rstrip()  # Strip trailing spaces

                # Normalize indentation by detecting the minimum leading spaces
                lines = code_block.split('\n')
                min_indent = min((len(line) - len(line.lstrip()) for line in lines if line.strip()), default=0)
                normalized_code_block = "\n".join(line[min_indent:] for line in lines)

                parsed_segments.append(('code_block', f"{language}\n{normalized_code_block}"))
            elif match.group(3) is not None:  # Headers
                header_level = len(match.group(3))
                header_content = match.group(4).strip()
                parsed_segments.append((f'header{header_level}', header_content))
            elif match.group(5) is not None:  # Bold
                parsed_segments.append(('bold', match.group(5).strip()))
            elif match.group(6) is not None:  # Italic
                parsed_segments.append(('italic', match.group(6).strip()))
            elif match.group(7) is not None:  # List item
                parsed_segments.append(('bullet', match.group(7).strip()))
            elif match.group(8) is not None:  # Link
                parsed_segments.append(('link', f"{match.group(8).strip()} ({match.group(9).strip()})"))
            elif match.group(10) is not None:  # Inline code
                parsed_segments.append(('inline_code', match.group(10).strip()))

        return parsed_segments


    def print_markdown(self, *args: Any, sep: str = ' ', end: str = '\n', filename: str = None, **kwargs):
        converted_args = [str(arg) for arg in args] if self.config["args_to_strings"] else args

        markdown_segments = []
        for arg in converted_args:
            markdown_segments.extend(self.parse_markdown(arg))

        styled_output = []
        for style_type, content in markdown_segments:
            if content.strip():  # Skip empty content
                if style_type == 'header1':
                    styled_output.append(self.apply_markdown_style('header1', content))
                elif style_type == 'header2':
                    styled_output.append(self.apply_markdown_style('header2', content))
                elif style_type == 'bold':
                    styled_output.append(self.apply_markdown_style('bold', content))
                elif style_type == 'italic':
                    styled_output.append(self.apply_markdown_style('italic', content))
                elif style_type == 'bullet':
                    styled_output.append(self.apply_markdown_style('bullet', f"- {content}"))
                elif style_type == 'link':
                    styled_output.append(self.apply_markdown_style('link', content))
                elif style_type == 'inline_code':
                    styled_output.append(self.apply_markdown_style('inline_code', content))
                elif style_type == 'code_block':  # Ensure code block is styled and printed
                    styled_output.append(self.apply_markdown_style('code_block', content))

        # Join the styled output and proceed with regular printing
        output = sep.join(styled_output)

        # Print or write to file
        if filename:
            with open(filename, 'a') as file:
                file.write(output + end)
        else:
            print(output, end=end)
        return


    def write(self, *control_keys_or_text, **kwargs):
        """
        Writes control sequences or text passed as arguments to sys.stdout.
        If the control sequence has formatting placeholders, it uses the kwargs for formatting.
        """
        for item in control_keys_or_text:
            if isinstance(item, str):
                # Check if the item is a control key in the ctl_map
                control_sequence = self.ctl_map.get(item, item)  # If not found, treat it as plain text
                # If there are kwargs like row, col, format the control sequence
                if kwargs and '{' in control_sequence and '}' in control_sequence:
                    control_sequence = control_sequence.format(**kwargs)
                sys.stdout.write(control_sequence)
        sys.stdout.flush()




def get_default_printer() -> Any:
    p = PrintsCharming()
    return p.print





