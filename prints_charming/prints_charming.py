# prints_charming.py

import time
import os
import pty
import sys
import subprocess
import threading
import asyncio
import termios
import tty
import select
import copy
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
    DEFAULT_CONTROL_MAP,
    DEFAULT_BYTE_MAP,
)

from .regex_patterns import (
    ansi_escape_patterns,
    LEADING_WS_PATTERN,
    WORDS_AND_SPACES_PATTERN,
)

from .prints_style import PStyle
from .prints_ui import PrintsUI
from .utils import compute_bg_color_map
from .trie_manager import TrieManager
from .markdown_processor import MarkdownProcessor
from .formatter import Formatter
from .internal_logging_utils import shared_logger
from .terminal_size_watcher import TerminalSizeWatcher
from .segment_styler import SegmentStyler
from .progress_bar import PBar

if sys.platform == 'win32':
    from .win_utils import WinUtils






def get_variable_name_from_stack(value, f_back_num=1):
    """
    Attempts to retrieve the name of a variable holding the given value from the calling stack.

    :param value: The value to find the variable name for.
    :param f_back_num: How many frames back to look for the variable name.
    :return: The name of the variable, if found; otherwise, None.
    """
    frame = inspect.currentframe()
    for _ in range(f_back_num + 1):  # Traverse back the specified number of frames
        frame = frame.f_back
        if frame is None:
            break
    if frame:
        names = [name for name, val in frame.f_locals.items() if val is value]
        return names[0] if names else None
    return None







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
    within the library, such as logging, exception handling, tables, frames,
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

    leading_ws_pattern = LEADING_WS_PATTERN
    words_and_spaces_pattern = WORDS_AND_SPACES_PATTERN

    # Dictionary of ansi escape patterns
    ansi_escape_patterns = ansi_escape_patterns

    # Default ansi escape pattern
    ansi_escape_pattern = ansi_escape_patterns['sgr_mk']

    is_alt_buffer = False  # Track current buffer state

    # Add locks for thread safety
    _write_lock = threading.Lock()  # For synchronous workflows
    _async_lock = asyncio.Lock()  # For asynchronous workflows




    @classmethod
    def update_default_ansi_escape_pattern(cls, pattern_key: str) -> None:
        """
        Update the default ANSI escape pattern used by the class.

        :param pattern_key: The key of the pattern to set as the default.
        :raises ValueError: If the provided pattern_key does not exist in ansi_escape_patterns.
        """
        # Retrieve the pattern
        pattern = ansi_escape_patterns.get(pattern_key)

        # Validate the pattern key
        if pattern is None:
            raise ValueError(
                f"Invalid pattern_key '{pattern_key}'. "
                f"Available keys are: {list(ansi_escape_patterns.keys())}."
            )

        # Update the default pattern
        cls.ansi_escape_pattern = pattern


    @classmethod
    def remove_ansi_codes(cls, text: Any, pattern_key: str = None) -> str:
        """
        Removes ANSI codes from the text.

        :param text: The input text (should be a string).
        :param pattern_key: (Optional) Key in ansi_escape_patterns dict.
                            If None, uses the default pattern (`cls.ansi_escape_pattern`).
        :return: The text without ANSI codes.
        :raises ValueError: If an invalid `pattern_key` is provided.
        """

        # Use the default pattern if no pattern_key is provided
        if not pattern_key:
            return cls.ansi_escape_pattern.sub('', text)

        # Retrieve the pattern for the provided key
        pattern = ansi_escape_patterns.get(pattern_key)
        if not pattern:
            raise ValueError(
                f"Invalid pattern_key '{pattern_key}'. "
                f"Available keys are: {list(ansi_escape_patterns.keys())}."
            )

        # Use the retrieved pattern to remove ANSI codes
        return pattern.sub('', text)


    _shared_instance = None
    _shared_instances = {}

    shared_color_map: Optional[Dict[str, str]] = None
    shared_bg_color_map: Optional[Dict[str, str]] = None
    shared_effect_map: Optional[Dict[str, str]] = DEFAULT_EFFECT_MAP
    shared_unicode_map: Optional[Dict[str, str]] = DEFAULT_UNICODE_MAP
    shared_styles: Optional[Dict[str, PStyle]] = None
    shared_ctl_map: Optional[Dict[str, str]] = DEFAULT_CONTROL_MAP
    shared_byte_map: Optional[Dict[str, bytes]] = DEFAULT_BYTE_MAP


    # Assigned with create_reverse_input_mapping classmethod called in relevant modules
    shared_reverse_input_map: Optional[Dict[bytes, str]] = None


    log_level_style_names: List[str] = ['debug', 'info', 'warning', 'error', 'critical']


    @classmethod
    def get_shared_instance(cls, key: str) -> Optional["PrintsCharming"]:
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
    def set_shared_instance(cls, key: str, instance: "PrintsCharming") -> None:
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


    @classmethod
    def set_shared_maps(cls,
                        shared_color_map: Optional[Dict[str, str]] = None,
                        shared_effect_map: Optional[Dict[str, str]] = None,
                        shared_unicode_map: Optional[Dict[str, str]] = None,
                        shared_style_map: Optional[Dict[str, PStyle]] = None,
                        shared_ctl_map: Optional[Dict[str, str]] = None,
                        shared_byte_map: Optional[Dict[str, bytes]] = None,
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

        :param shared_effect_map: (Optional) A dictionary of effect mappings.
                                  **This should not be changed unless you are
                                  certain of what you're doing.**

        :param shared_unicode_map: (Optional) A dictionary of unicode mappings.

        :param shared_style_map: (Optional) A dictionary of shared styles. This
                                 allows for the consistent application of styles
                                 across all instances.

        :param shared_ctl_map: (Optional) A dictionary of shared control codes.
        :param shared_byte_map: (Optional) A dictionary of bytes for input parsing.
        """

        cls.shared_color_map = shared_color_map or DEFAULT_COLOR_MAP.copy()
        cls.shared_color_map.setdefault('default', PrintsCharming.RESET)
        cls.shared_bg_color_map = {
            color: compute_bg_color_map(code)
            for color, code in cls.shared_color_map.items()
        }

        if shared_effect_map:
            cls.shared_effect_map = shared_effect_map

        if shared_unicode_map:
            cls.shared_unicode_map = shared_unicode_map

        if shared_style_map:
            cls.shared_styles = shared_style_map

        if shared_ctl_map:
            cls.shared_ctl_map = shared_ctl_map

        if shared_byte_map:
            cls.shared_byte_map = shared_byte_map


    @classmethod
    def create_reverse_input_mapping(
            cls,
            ctl_map_input_keys: Optional[set] = None,
            byte_map_input_keys: Optional[set] = None,
            update: bool = False,
    ) -> None:
        """
        Create a reverse input mapping for escape sequences.

        Args:
            ctl_map_input_keys (Optional[set]): Keys from shared_ctl_map to include.
            byte_map_input_keys (Optional[set]): Keys from shared_byte_map to include.
            update (bool): If True, updates the existing mapping; otherwise, rebuilds it.
        """
        if cls.shared_reverse_input_map is None or update:
            ctl_map_input_keys = ctl_map_input_keys or set(cls.shared_ctl_map.keys())
            byte_map_input_keys = byte_map_input_keys or set(cls.shared_byte_map.keys())

            # Combine control and byte maps, filter out placeholder sequences
            cls.shared_reverse_input_map = {
                (v.encode() if isinstance(v, str) else v): k
                for k, v in {**cls.shared_ctl_map, **cls.shared_byte_map}.items()
                if (k in ctl_map_input_keys or k in byte_map_input_keys)
                and not (isinstance(v, str) and "{" in v and "}" in v)  # Exclude placeholders
            }


    @staticmethod
    def read_input() -> Optional[bytes]:
        """Read input from stdin in a non-blocking way."""
        fd = sys.stdin.fileno()
        rlist, _, _ = select.select([sys.stdin], [], [], 0)
        if sys.stdin in rlist:
            return sys.stdin.buffer.read(1)
        else:
            return None


    @classmethod
    def parse_input(cls) -> Tuple[Optional[str], Optional[Any]]:
        """Parse input and determine if it's a mouse event, keystroke, or escape sequence."""
        c = cls.read_input()
        if c is None:
            return None, None

        if c == cls.shared_byte_map['escape_key']:  # Start of an escape sequence
            c += sys.stdin.buffer.read(1)
            if c[-1:] == b'[':
                c += sys.stdin.buffer.read(1)
                if c[-1:] == cls.shared_byte_map['mouse_event_start']:
                    # Mouse event
                    seq = c + cls.read_mouse_event_sequence()
                    mouse_event = cls.parse_mouse_event(seq)
                    return 'mouse', mouse_event
                else:
                    # Other escape sequence
                    seq = c + cls.read_remaining_escape_sequence()
                    keystroke = cls.parse_escape_sequence(seq)
                    return 'keystroke', keystroke
            else:
                # Single ESC keypress or other sequence
                return 'keystroke', 'ESCAPE'
        else:
            # Regular keystroke
            try:
                ch = c.decode('utf-8', errors='ignore')
                return 'keystroke', ch
            except UnicodeDecodeError:
                return None, None

    @classmethod
    def read_mouse_event_sequence(cls) -> bytes:
        """Read the remaining bytes of a mouse event sequence."""
        seq = b''
        while True:
            ch = sys.stdin.buffer.read(1)  # Blocking read
            seq += ch
            if ch in (
                    cls.shared_byte_map['mouse_event_end_press'],
                    cls.shared_byte_map['mouse_event_end_release']
            ):
                break
        return seq

    @classmethod
    def read_remaining_escape_sequence(cls) -> bytes:
        """Read the remaining bytes of an escape sequence."""
        seq = b''
        while True:
            ch = sys.stdin.buffer.read(1)  # Blocking read
            seq += ch
            if ch.isalpha() or ch == b'~':
                break
        return seq


    @staticmethod
    def parse_mouse_event(seq: bytes) -> Optional[Tuple[int, int, int, bytes]]:
        """Parse a mouse event from the given sequence."""
        # Expected format: '\x1b[<b;x;yM' or '\x1b[<b;x;ym'
        try:
            params = seq[3:-1].split(b';')
            if len(params) == 3:
                b_code = int(params[0])
                x = int(params[1])
                y = int(params[2])
                event_type = seq[-1:]  # b'M' for press, b'm' for release
                return b_code, x, y, event_type
            else:
                return None
        except ValueError:
            return None

    # Reverse Lookup Function
    @classmethod
    def parse_escape_sequence(cls, seq: bytes, default: str = "ESCAPE") -> str:
        """Parse other escape sequences"""
        if not cls.shared_reverse_input_map:
            cls.create_reverse_input_mapping()
        return cls.shared_reverse_input_map.get(seq, default)


    @classmethod
    def set_log_level_style_names(cls, levels: List[str]) -> None:
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


    @classmethod
    def clear_line(cls, use_carriage_return: bool = True) -> None:
        if use_carriage_return:
            print("\r" + cls.shared_ctl_map["clear_line"], end='')
        else:
            print(cls.shared_ctl_map["clear_line"], end='')


    @classmethod
    def write(
        cls,
        *control_keys_or_text: Union[str, bytes],
        dynamic_state_handling: bool = True,
        track_alt_buffer_state: bool = True,
        **kwargs: Any
    ) -> None:
        """
        Synchronous method to write control sequences or text to sys.stdout.

        :param dynamic_state_handling: Enable advanced handling of interleaved buffer transitions.
        :param track_alt_buffer_state: Track and update the buffer state (alt_buffer or normal_buffer).
        """
        with cls._write_lock:
            cls._write_internal(
                control_keys_or_text,
                dynamic_state_handling=dynamic_state_handling,
                track_alt_buffer_state=track_alt_buffer_state,
                kwargs=kwargs
            )


    @classmethod
    async def write_async(
        cls,
        *control_keys_or_text: Union[str, bytes],
        dynamic_state_handling: bool = True,
        track_alt_buffer_state: bool = True,
        use_queue: bool = False,
        queue: Optional[asyncio.Queue] = None,
        batch_size: int = 0,
        max_batch_size: int = 50,
        min_batch_size: int = 5,
        **kwargs: Any
    ) -> None:
        """
        Asynchronous method to write control sequences or text to sys.stdout with optional queue-based processing.

        :param dynamic_state_handling: Enable advanced handling of interleaved buffer transitions.
        :param track_alt_buffer_state: Track and update the buffer state (alt_buffer or normal_buffer).
        :param use_queue: Enable queue-based buffering of output.
        :param queue: An optional asyncio.Queue instance for custom queue management.
        :param batch_size: Number of items to process per batch in queue-based mode.
        """
        if use_queue:
            if not queue:
                queue = asyncio.Queue()  # Create a default queue if not provided
            await cls._process_queue(queue, batch_size, max_batch_size, min_batch_size, dynamic_state_handling, track_alt_buffer_state, kwargs)
        else:
            await cls._write_internal_async(
                control_keys_or_text,
                dynamic_state_handling=dynamic_state_handling,
                track_alt_buffer_state=track_alt_buffer_state,
                kwargs=kwargs
            )


    @classmethod
    async def _process_queue(
        cls,
        queue: asyncio.Queue,
        batch_size: Optional[int],
        max_batch_size: Optional[int],
        min_batch_size: Optional[int],
        dynamic_state_handling: bool,
        track_alt_buffer_state: bool,
        kwargs: Any
    ) -> None:
        """
        Process items in an asyncio.Queue in batches.
        """
        while not queue.empty():
            # Dynamically calculate the effective batch size
            effective_batch_size = batch_size or min(max(queue.qsize() // 2, min_batch_size), max_batch_size)

            # Collect items for this batch
            items = []
            for _ in range(min(effective_batch_size, queue.qsize())):
                items.append(await queue.get())

            async with cls._async_lock:
                await cls._write_internal_async(items, dynamic_state_handling, track_alt_buffer_state, kwargs)


    @classmethod
    def _write_internal(
        cls,
        control_keys_or_text: Union[List[Any], Any],
        dynamic_state_handling: bool,
        track_alt_buffer_state: bool,
        kwargs: Any
    ) -> None:
        """
        Internal method to handle writing logic with support for both synchronous and asynchronous workflows.
        """


        if dynamic_state_handling:
            # Advanced method: Handles dynamic buffer state transitions
            current_state = cls.is_alt_buffer if track_alt_buffer_state else None
            output_buffer = []

            for item in control_keys_or_text:
                if item == 'alt_buffer':
                    if track_alt_buffer_state and not current_state:  # Transition to alt_buffer
                        cls.is_alt_buffer = True
                        current_state = True
                    # Flush the current buffer
                    if output_buffer:
                        cls._flush_buffer(output_buffer)
                        output_buffer = []
                    cls._write_direct(cls.shared_ctl_map.get('alt_buffer', ''))
                elif item == 'normal_buffer':
                    if track_alt_buffer_state and current_state:  # Transition to normal_buffer
                        cls.is_alt_buffer = False
                        current_state = False
                    # Flush the current buffer
                    if output_buffer:
                        cls._flush_buffer(output_buffer)
                        output_buffer = []
                    cls._write_direct(cls.shared_ctl_map.get('normal_buffer', ''))
                else:
                    # Handle regular text or control sequences
                    if isinstance(item, str):
                        control_sequence = cls.shared_ctl_map.get(item, item)
                        if kwargs and '{' in control_sequence and '}' in control_sequence:
                            control_sequence = control_sequence.format(**kwargs)
                        output_buffer.append(control_sequence)

            # Flush remaining output
            if output_buffer:
                cls._flush_buffer(output_buffer)

        else:
            # Simpler method: Assumes no interleaved buffer transitions
            if track_alt_buffer_state:
                if 'alt_buffer' in control_keys_or_text:
                    cls.is_alt_buffer = True
                elif 'normal_buffer' in control_keys_or_text:
                    cls.is_alt_buffer = False

            # Collect and write output
            for item in control_keys_or_text:
                if isinstance(item, str):
                    # Check if the item is a control key in the ctl_map
                    control_sequence = cls.shared_ctl_map.get(item, item)  # If not found, treat it as plain text
                    # If there are kwargs like row, col, format the control sequence
                    if kwargs and '{' in control_sequence and '}' in control_sequence:
                        control_sequence = control_sequence.format(**kwargs)
                    sys.stdout.write(control_sequence)
            sys.stdout.flush()


    @classmethod
    async def _write_internal_async(
        cls,
        control_keys_or_text: Union[List[Any], Any],
        dynamic_state_handling: bool,
        track_alt_buffer_state: bool,
        kwargs: Any
    ) -> None:
        """
        Internal method to handle writing logic with support for both synchronous and asynchronous workflows.
        """

        if dynamic_state_handling:
            # Advanced method: Handles dynamic buffer state transitions
            current_state = cls.is_alt_buffer if track_alt_buffer_state else None
            output_buffer = []

            for item in control_keys_or_text:
                if item == 'alt_buffer' and not current_state:  # Transition to alt_buffer
                    async with cls._async_lock:
                        cls.is_alt_buffer = True
                        current_state = True
                        if output_buffer:
                            await cls._flush_buffer_async(output_buffer, True)  # Flush buffered content
                            output_buffer = []
                        await cls._write_direct_async(cls.shared_ctl_map.get('alt_buffer', ''))
                elif item == 'normal_buffer' and current_state:  # Transition to normal_buffer
                    async with cls._async_lock:
                        cls.is_alt_buffer = False
                        current_state = False
                        if output_buffer:
                            await cls._flush_buffer_async(output_buffer, True)  # Flush buffered content
                            output_buffer = []
                        await cls._write_direct_async(cls.shared_ctl_map.get('normal_buffer', ''))
                else:
                    # Buffer regular text or control sequences
                    if isinstance(item, str):
                        control_sequence = cls.shared_ctl_map.get(item, item)
                        if kwargs and '{' in control_sequence and '}' in control_sequence:
                            control_sequence = control_sequence.format(**kwargs)
                        output_buffer.append(control_sequence)

            # Final flush of any remaining output
            if output_buffer:
                async with cls._async_lock:  # Lock for final flush
                    await cls._flush_buffer_async(output_buffer, True)

        else:
            # Simpler method: Assumes no interleaved buffer transitions
            if track_alt_buffer_state:
                if 'alt_buffer' in control_keys_or_text:
                    cls.is_alt_buffer = True
                elif 'normal_buffer' in control_keys_or_text:
                    cls.is_alt_buffer = False

            # Collect and write output
            for item in control_keys_or_text:
                if isinstance(item, str):
                    # Check if the item is a control key in the ctl_map
                    control_sequence = cls.shared_ctl_map.get(item, item)  # If not found, treat it as plain text
                    # If there are kwargs like row, col, format the control sequence
                    if kwargs and '{' in control_sequence and '}' in control_sequence:
                        control_sequence = control_sequence.format(**kwargs)
                    sys.stdout.write(control_sequence)
            sys.stdout.flush()


    @classmethod
    def _flush_buffer(cls, output_buffer: List[str], force_flush: bool = False) -> None:
        """
        Flushes the output buffer to sys.stdout, consolidating flushes when possible.
        """
        if not output_buffer and not force_flush:
            return  # No flush needed
        sys.stdout.write(''.join(output_buffer))
        sys.stdout.flush()


    @classmethod
    async def _flush_buffer_async(cls, output_buffer: List[str], force_flush: bool = False) -> None:
        """
        Flushes the output buffer to sys.stdout, consolidating flushes when possible.
        """
        if not output_buffer and not force_flush:
            return  # No flush needed
        await asyncio.to_thread(sys.stdout.write, ''.join(output_buffer))
        await asyncio.to_thread(sys.stdout.flush)


    @classmethod
    def _write_direct(cls, text: str) -> None:
        """
        Writes directly to sys.stdout.
        """
        sys.stdout.write(text)


    @classmethod
    async def _write_direct_async(cls, text: str) -> None:
        """
        Writes directly to sys.stdout.
        """
        await asyncio.to_thread(sys.stdout.write, text)



    @classmethod
    def write_orig(cls, *control_keys_or_text: Union[str, bytes], **kwargs: Any) -> None:
        """
        Writes control sequences or text passed as arguments to sys.stdout.
        If the control sequence has formatting placeholders, it uses the kwargs for formatting.
        """
        if 'alt_buffer' in control_keys_or_text:
            cls.is_alt_buffer = True
        elif 'normal_buffer' in control_keys_or_text:
            cls.is_alt_buffer = False
        for item in control_keys_or_text:
            if isinstance(item, str):
                # Check if the item is a control key in the ctl_map
                control_sequence = cls.shared_ctl_map.get(item, item)  # If not found, treat it as plain text
                # If there are kwargs like row, col, format the control sequence
                if kwargs and '{' in control_sequence and '}' in control_sequence:
                    control_sequence = control_sequence.format(**kwargs)
                sys.stdout.write(control_sequence)
        sys.stdout.flush()


    @classmethod
    def render_output(cls, *control_keys_or_text: Union[str, bytes, tuple], **global_kwargs: Any) -> None:
        """
        Writes control sequences or text to sys.stdout.
        Positional arguments can include tuples for scoped control sequences.
        """
        output = []
        for item in control_keys_or_text:
            if isinstance(item, tuple):
                # Unpack the tuple: (control_key, local_kwargs)
                key, local_kwargs = item
                control_sequence = cls.shared_ctl_map.get(key, key)
                if local_kwargs:
                    control_sequence = control_sequence.format(**local_kwargs)
                output.append(control_sequence)
            elif isinstance(item, str):
                control_sequence = cls.shared_ctl_map.get(item, item)
                if global_kwargs and '{' in control_sequence and '}' in control_sequence:
                    control_sequence = control_sequence.format(**global_kwargs)
                output.append(control_sequence)
            elif isinstance(item, bytes):
                output.append(item.decode("utf-8"))
        sys.stdout.write("".join(output))
        sys.stdout.flush()




    def __init__(self,
                 config: Optional[Dict[str, Union[bool, int, str]]] = None,
                 color_map: Optional[Dict[str, str]] = None,
                 default_bg_color: Optional[str] = None,
                 effect_map: Optional[Dict[str, str]] = None,
                 unicode_map: Optional[Dict[str, str]] = None,
                 styles: Optional[Dict[str, PStyle]] = None,
                 enable_input_parsing: bool = False,
                 enable_term_size_watcher: bool = False,
                 enable_trie_manager: bool = True,
                 styled_strings: Optional[Dict[str, List[str]]] = None,
                 styled_subwords: Optional[Dict[str, List[str]]] = None,
                 enable_markdown: bool = False,
                 terminal_mode: str = "single",
                 style_conditions: Optional[Any] = None,
                 formatter: Optional['Formatter'] = None,
                 ) -> None:

        """
        Initialize PrintsCharming with args to any of these optional params.

        :param config: enable or disable various functionalities of this class.

        :param color_map: supply your own color_map dictionary.
                          'color_name': 'ansi_code'

        :param default_bg_color: change the default background color to a color
                                 other than your terminal's background color by
                                 supplying the name of a color defined in the
                                 color map.

        :param effect_map: supply your own effect_map dictionary. Default is
                           PrintsCharming.shared_effect_map

        :param unicode_map: supply your own unicode_map dictionary. Default is
                            PrintsCharming.shared_unicode_map

        :param styles: supply your own style_map dictionary. Default is a copy
                       of the DEFAULT_STYLES dictionary unless
                       cls.shared_style_map is defined.

        :param enable_input_parsing: if True define cls.shared_reverse_input_map
                       by calling self.__class__.create_reverse_input_mapping()

        :param enable_term_size_watcher: if True initializes an instance of
                                         TerminalSizeWatcher passing self to
                                         the pc param.

        :param enable_trie_manager: if True initializes an instance of
                                    TrieManager passing self to the pc_instance
                                    param.

        :param enable_markdown: if True initializes an instance of
                                MarkdownProcessor passing self to the
                                pc_instance param.

        :param styled_strings: calls the add_strings_from_dict method with your
                               provided styled_strings dictionary.

        :param styled_subwords: calls the add_subwords_from_dict method with your
                               provided styled_subwords dictionary.

        :param style_conditions: A custom class for implementing dynamic
                                 application of styles to text based on
                                 conditions.

        :param formatter: supply your own formatter class instance to be used
                          for formatting text printed using the print method in
                          this class.
        """

        self.config = {**DEFAULT_CONFIG, **(config or {})}

        self.color_map = (
            color_map
            or PrintsCharming.shared_color_map
            or DEFAULT_COLOR_MAP.copy()
        )
        self.color_map.setdefault('default', PrintsCharming.RESET)

        self.bg_color_map = {
                color: compute_bg_color_map(code)
                for color, code in self.color_map.items()
        }

        self.effect_map = effect_map or PrintsCharming.shared_effect_map

        self.unicode_map = unicode_map or PrintsCharming.shared_unicode_map

        self.ctl_map = PrintsCharming.shared_ctl_map

        self.byte_map = PrintsCharming.shared_byte_map

        if enable_input_parsing:
            self.__class__.create_reverse_input_mapping()

        self.enable_term_size_watcher = enable_term_size_watcher

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


        self.reset = PrintsCharming.RESET

        self.win_utils = None
        if sys.platform == 'win32':
            self.win_utils = WinUtils
            if not WinUtils.is_ansi_supported_natively():
                if not WinUtils.enable_win_console_ansi_handling():
                    logging.error("Failed to enable ANSI handling on Windows")

        self.terminal_width = None
        self.terminal_height = None

        self.terminal_mode = terminal_mode

        self.terminals = {}  # For managing multiple terminals
        self.single_terminal_config = {"title": "PrintsCharming Terminal"}

        self.term_size_watcher = TerminalSizeWatcher(self)

        self.trie_manager = None
        if enable_trie_manager:
            self.trie_manager = TrieManager(self)

            if styled_strings:
                self.trie_manager.add_strings_from_dict(styled_strings)
            if styled_subwords:
                self.trie_manager.add_subwords_from_dict(styled_subwords)


        self.markdown_processor = None
        if enable_markdown:
            self.markdown_processor = MarkdownProcessor(self)

        self.sentence_ending_characters = ".,!?:;"

        self.style_conditions = style_conditions
        self.style_conditions_map = {}
        if style_conditions:
            self.style_conditions_map = style_conditions.map

        self.style_cache = {}


        # Instance-level flag to control logging
        self.internal_logging_enabled = (
            self.config.get("internal_logging", False)
        )

        # Use shared logger but don't disable it
        self.logger = shared_logger
        self.setup_internal_logging(self.config.get("log_level", "DEBUG"))

        self.formatter = formatter or Formatter()

        self.segment_styler = SegmentStyler(self)

        if terminal_mode == "single":
            self._setup_single_terminal()





    def _setup_single_terminal(self):
        """Setup configurations for single-terminal mode."""
        self.single_terminal_streams = {
            "stdout": sys.stdout,
            "stdin": sys.stdin,
        }
        self.write("set_window_title", title=self.single_terminal_config["title"])


    def launch_terminal(self, name, terminal_emulator="gnome-terminal", width=80, height=24, title="New Terminal", task=None):
        """
        Launch a new terminal with a given task.
        """
        if self.terminal_mode != "multi":
            raise RuntimeError("Multi-terminal mode is not enabled.")

        master_fd, slave_fd = pty.openpty()
        terminal_cmd = [
            terminal_emulator,
            "--geometry", f"{width}x{height}",
            "--", "bash", "-c", "cat",
        ]
        subprocess.Popen(
            terminal_cmd,
            stdin=slave_fd,
            stdout=slave_fd,
            stderr=slave_fd,
            close_fds=True,
        )
        os.close(slave_fd)

        time.sleep(0.5)  # Allow terminal to initialize

        # Store the terminal instance
        self.terminals[name] = master_fd

        # Redirect sys.stdout to the new terminal for the task
        sys.stdout = os.fdopen(master_fd, "w")
        sys.stdin = os.fdopen(master_fd, "r")
        self.write("alt_buffer")
        self.write("set_window_title", title=title)

        # Run the task in a separate thread
        if task:
            threading.Thread(target=task, args=(master_fd,)).start()


    def restore_terminal(self, name=None):
        """
        Restore a specific terminal or all terminals if no name is provided.
        """
        if name:
            self._restore_single_terminal(name)
        else:
            for terminal_name in list(self.terminals.keys()):
                self._restore_single_terminal(terminal_name)


    def _restore_single_terminal(self, name):
        """
        Restore and close a specific terminal.
        """
        master_fd = self.terminals.get(name)
        if master_fd:
            sys.stdout = sys.__stdout__  # Restore to original stdout
            self.write("normal_buffer")
            os.close(master_fd)
            del self.terminals[name]


    def single_terminal_task(self):
        """Example task for single-terminal mode."""
        self.write("Welcome to the single terminal mode!\n")
        while True:
            try:
                self.write("\nEnter a command (type 'exit' to quit): ")
                command = input()
                if command.lower() == "exit":
                    break
                self.write(f"You entered: {command}\n")
            except KeyboardInterrupt:
                break


    def write_multi_terminal(self, master_fd: int, *control_keys_or_text: Union[str, bytes], **kwargs: Any):
        """
        Multi-terminal task that writes control sequences or text to the terminal's stdout.

        Args:
            master_fd (int): The file descriptor of the master end of the pseudo-terminal.
            *control_keys_or_text (Union[str, bytes]): Control sequences or text to be written to the terminal.
            **kwargs: Formatting options for the control sequences.
        """
        try:
            # Redirect stdout to the master file descriptor
            with os.fdopen(master_fd, "w") as terminal_output:
                sys.stdout = terminal_output

                # Write the content to the terminal using the `write` method
                self.write(*control_keys_or_text, **kwargs)
        finally:
            # Restore the original stdout
            sys.stdout = sys.__stdout__



    def get_progress_bar(self, total: int, desc: str = "", width: int = 40, style: str = "progress", mode="auto"):
        return PBar(self, total, desc, width, style, mode)



    def escape_ansi_codes(self, ansi_string: str, escape_to: str = "\\x1b") -> str:
        """
        Escapes ANSI escape codes in a given string, replacing them with a specified escape sequence.

        :param ansi_string: The string containing ANSI escape codes.
        :param escape_to: The string to replace the ANSI escape code with. Default is '\\033'.
        :return: The string with escaped ANSI codes replaced as specified.
        """
        self.debug(
            "Escaping ANSI codes in string: {}",
            ansi_string
        )
        escaped_ansi_string = ansi_string.replace("\x1b", escape_to)
        self.debug(
            "Escaped ANSI codes in string: {}",
            escaped_ansi_string
        )

        return escaped_ansi_string


    def create_style_code(self, style: Union[PStyle, Dict[str, Any]]) -> str:
        """
        Creates the ANSI style code for the given style.

        :param style: A `PStyle` instance or a dictionary defining the style.
        :return: The ANSI escape sequence for the style.
        """
        style_codes: List[str] = []

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


    def add_style(self, name: str, style: PStyle) -> None:
        """
        Add a new style, applying self.default_bg_color only if no bg_color is specified
        and self.default_bg_color is defined.

        :param name: The name of the style.
        :param style: A `PStyle` instance defining the style.
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

        :param styles: A dictionary where keys are style names and values are `PStyle` instances.
        """
        for style_name, style in styles.items():
            # Apply default background color if none is specified and self.default_bg_color is set
            if (not hasattr(style, 'bg_color') or style.bg_color is None) and self.default_bg_color:
                style.bg_color = self.default_bg_color

            if style.color in self.color_map:
                self.add_style(style_name, style)


    def edit_style(self, name: str, new_style: Union[PStyle, Dict[str, Any]]) -> None:
        """
        Edit an existing style by updating its attributes and regenerating its ANSI code,
        applying the default background color if not specified.

        :param name: The name of the style to edit.
        :param new_style: A `PStyle` instance or a dictionary with new attributes.
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


    def edit_styles(self, new_styles: Dict[str, Union[PStyle, Dict[str, Any]]]) -> None:
        """
        Edit multiple styles by updating each style's attributes and regenerating their ANSI codes,
        applying the default background color if not specified.

        :param new_styles: A dictionary of style names to `PStyle` instances or dictionaries.
        """
        for name, new_style in new_styles.items():
            if name not in self.styles:
                raise ValueError(f"Style '{name}' does not exist.")

            # Use edit_style to apply the default background color as necessary
            self.edit_style(name, new_style)


    def rename_style(self, current_name: str, new_name: str) -> None:
        """
        Rename an existing style in both self.styles and self.style_codes.

        :param current_name: The current name of the style.
        :param new_name: The new name for the style.
        """
        if current_name not in self.styles:
            raise ValueError(f"Style '{current_name}' does not exist.")
        if new_name in self.styles:
            raise ValueError(f"Style '{new_name}' already exists.")

        # Move style and its code to the new name
        self.styles[new_name] = self.styles.pop(current_name)
        if current_name in self.style_codes:
            self.style_codes[new_name] = self.style_codes.pop(current_name)


    def rename_styles(self, name_map: dict[str, str]) -> None:
        """
        Rename multiple styles using a mapping from current names to new names.

        :param name_map: A dictionary mapping current style names to new names.
        """
        for current_name, new_name in name_map.items():
            self.rename_style(current_name, new_name)


    def remove_style(self, name: str) -> None:
        """
        Remove a style by its name from both self.styles and self.style_codes.

        :param name: The name of the style to remove.
        """
        if name in self.styles:
            del self.styles[name]
            if name in self.style_codes:
                del self.style_codes[name]
        else:
            raise ValueError(f"Style '{name}' does not exist.")


    def remove_styles(self, names: list[str]) -> None:
        """
        Remove multiple styles by their names from both self.styles and self.style_codes.

        :param names: A list of style names to remove.
        """
        for name in names:
            self.remove_style(name)


    def get_style_code(self, style_name: str) -> str:
        """
        Retrieves the ANSI style code for the given style name.

        :param style_name: The name of the style.
        :return: The ANSI style code for the style, or the default style code if the style is not found.
        """
        return self.style_codes.get(style_name, self.style_codes['default'])


    def apply_style_code(self, code: str, text: Any, reset: bool = True) -> str:
        """
        Applies a given ANSI style code to the provided text.

        :param code: The ANSI style code to apply.
        :param text: The text to style.
        :param reset: Whether to reset styles after the text.
        :return: The styled text with the applied ANSI code.
        """
        return f'{code}{text}{self.reset if reset else ''}'



    def apply_style(self, style_name: str, text: Any, fill_space: bool = True, fill_bg_only: bool = True, reset: bool = True) -> str:
        """
        Applies a style to the given text.

        :param style_name: The name of the style to apply.
        :param text: The text to style.
        :param fill_space: Whether to fill whitespace with the background color.
        :param fill_bg_only: Only fill bg_color attrib.
        :param reset: Whether to reset styles after the text.
        :return: The styled text.
        """
        self.debug(
            "Applying style_name: {} to text: {}",
            self._apply_style_internal('info', style_name),
            self._apply_style_internal('info', text)
        )

        text = str(text)
        if text.isspace() and fill_space:
            if fill_bg_only:
                style_code = self.bg_color_map.get(
                    style_name,
                    self.bg_color_map.get(
                        self.styles.get(style_name, 'default_bg').bg_color
                    )
                )
            else:
                style_code = self.style_codes.get(
                    style_name,
                    self.bg_color_map.get(
                        style_name,
                        self.bg_color_map.get('default')
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


    def apply_styles(self, strs_list: List[str], styles_list: Union[str, List[str]], sep: str = ' ', return_list: bool = False) -> Union[str, List[str]]:
        """
        Applies styles to a list of strings, optionally returning them as a list.

        :param strs_list: A list of strings to style.
        :param styles_list: A single style or a list of styles to apply.
        :param sep: The separator between joined list items.
        :param return_list: Whether to return a list of styled strings.
        :return: The styled strings as a single concatenated string or a list.
        """
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
        return sep.join(styled_strs) if not return_list else styled_strs


    def get_color_code(self, color_name: str) -> str:
        """
        Retrieves the ANSI color code for the given color name.

        :param color_name: The name of the color.
        :return: The ANSI color code for the color, or the default color code if the color is not found.
        """
        return self.color_map.get(color_name, self.color_map['default'])


    def apply_color(self, color_name: str, text: Any, fill_space: bool = True) -> str:
        """
        Applies a color to the given text.

        :param color_name: The name of the color.
        :param text: The text to apply the color to.
        :param fill_space: Whether to fill whitespace with the background color.
        :return: The text styled with the specified color.
        """
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


    def get_bg_color_code(self, color_name: str) -> str:
        """
        Retrieves the ANSI background color code for the given color name.

        :param color_name: The name of the background color.
        :return: The ANSI background color code, or None if the color is not found.
        """
        return self.bg_color_map.get(color_name)


    def apply_bg_color(self, color_name: str, text: Any) -> str:
        """
        Applies a background color to the given text.

        :param color_name: The name of the background color.
        :param text: The text to apply the background color to.
        :return: The text styled with the specified background color.
        """
        bg_color_code = self.get_bg_color_code(color_name)
        bg_color_block = f"{bg_color_code}{text}{self.reset}"

        return bg_color_block


    def get_effect_code(self, effect_name: str) -> str:
        """
        Retrieves the ANSI effect code for the given effect name.

        :param effect_name: The name of the effect.
        :return: The ANSI effect code, or an empty string if the effect is not found.
        """
        return self.effect_map.get(effect_name, '')


    def apply_effect(self, effect_name: str, text: Any) -> str:
        """
        Applies an effect to the given text.

        :param effect_name: The name of the effect.
        :param text: The text to apply the effect to.
        :return: The text styled with the specified effect.
        """
        effect_code = self.get_effect_code(effect_name)
        return f'{effect_code}{text}{self.reset}'


    def generate_bg_bar_strip(self, color_name: str, length: int = 10) -> str:
        """
        Generates a block of background color as a string.

        :param color_name: The name of the color as per self.bg_color_map.
        :param length: The length of the color block in terms of spaces.

        :return: A string representing the background color block.
        """
        self.debug("Generating background color strip: {} with length: {}", color_name, length)

        # Retrieve background color code
        bg_color_code = self.bg_color_map.get(color_name)

        # Generate and return the styled color block
        return f"{bg_color_code}{' ' * length}{self.reset}"


    def conceal_text(
        self,
        text_to_conceal: Any,
        replace: bool = False,
        replace_with: str = "***concealed_text***",
        style_name: Optional[str] = None
    ) -> str:

        """
        Conceals a given text, optionally replacing it with a placeholder.

        :param text_to_conceal: The text to conceal.
        :param replace: Whether to replace the text with a placeholder.
        :param replace_with: Placeholder string to replace concealed text with.
        :param style_name: The style to apply for concealment.
        :return: The concealed text.
        """
        if replace:
            style_code = self.style_codes.get(style_name)
            if not style_code:
                style_code = self.style_codes.get('conceal_replaced', self.style_codes.get('default'))
            concealed_text = f"{style_code}{replace_with}{self.reset}"
        else:
            style_code = self.style_codes.get('conceal')
            if not style_code:
                style_code = PrintsCharming.shared_effect_map.get('conceal')
            concealed_text = f"{style_code}{text_to_conceal}{self.reset}"

        return concealed_text


    def format_structure(self, structure: Any, indent: int = 4, prepend_fill: bool = True, pad_left_style: str = 'green', fill_to_end: bool = True, fill_bg_only: bool = False, include_var_name: bool = True, f_back_num: int = 1) -> str:
        """
        Formats and styles a structure (list, tuple, set, dict, or other nested data types) as a styled string.

        :param structure: The structure to format and style.
        :param indent: The number of spaces to use for indentation.
        :param include_var_name: If True, attempts to include the variable name.
        :param f_back_num: How many frames back to look for the variable name.
        :return: A string representing the formatted and styled structure.
        """

        def format_inner(structure: Any, level: int = 0) -> str:
            result = ""
            if isinstance(structure, dict):
                open_bracket = self.apply_style('python_bracket', '{')
                close_bracket = self.apply_style('python_bracket', '}')
                result += f"{open_bracket}\n"
                items = list(structure.items())
                for i, (key, value) in enumerate(items):
                    styled_colon = self.apply_style('python_colon', ":")
                    result += (
                            " " * ((level + 1) * indent) if not prepend_fill else self.apply_style(pad_left_style, " " * ((level + 1) * indent), fill_bg_only=fill_bg_only)
                            + self.apply_style('dict_key', f'"{key}"')
                            + styled_colon
                            + self.apply_style('default', " ", fill_bg_only=False)
                    )
                    result += format_inner(value, level + 1)
                    if i < len(items) - 1:  # Add a styled comma if not the last item
                        styled_comma = self.apply_style('python_comma', ",")
                        result = result.rstrip("\n") + styled_comma + "\n"
                result += " " * (level * indent) + close_bracket
            elif isinstance(structure, (list, tuple, set)):
                brackets = {
                    list: ("[", "]"),
                    tuple: ("(", ")"),
                    set: ("{", "}"),
                }
                open_bracket, close_bracket = map(lambda b: self.apply_style('python_bracket', b), brackets[type(structure)])
                result += f"{open_bracket}\n"
                items = list(structure)
                for i, item in enumerate(items):
                    result += (
                            " " * ((level + 1) * indent)
                            + format_inner(item, level + 1)
                    )
                    if i < len(items) - 1:  # Add a styled comma if not the last item
                        styled_comma = self.apply_style('python_comma', ",")
                        result = result.rstrip("\n") + styled_comma + "\n"
                result += " " * (level * indent) + close_bracket
            elif isinstance(structure, bool):
                bool_style = 'true' if structure else 'false'
                result += self.apply_style(bool_style, str(structure))
            elif structure is None:
                result += self.apply_style('none', str(structure))
            elif isinstance(structure, int):
                result += self.apply_style('int', str(structure))
            elif isinstance(structure, float):
                result += self.apply_style('float', str(structure))
            elif isinstance(structure, str):
                if (
                        structure.isupper()
                        and structure.lower() in self.__class__.log_level_style_names
                ):
                    result += self.apply_style(structure.lower(), structure)
                else:
                    result += self.apply_style('string', f'"{structure}"')
            else:
                result += self.apply_style('other', str(structure))
            return result.rstrip("\n") + "\n"

        formatted_structure = format_inner(structure).rstrip(",\n") + "\n"
        if include_var_name:
            var_name = get_variable_name_from_stack(structure, f_back_num)
            if var_name:
                styled_equal = self.apply_style('python_operator', ' = ')
                return f"{self.apply_style('python_variable', var_name)}{styled_equal}{formatted_structure}"
        return formatted_structure


    def format_dict(self, d: Dict[Any, Any], indent: int = 4) -> str:
        """
        Formats a dictionary as a styled string.

        :param d: The dictionary to format.
        :param indent: The number of spaces to use for indentation.
        :return: A string representing the formatted dictionary.
        """

        def pprint_dict(d: Dict[Any, Any], level: int = 0) -> str:
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
                        self.apply_style(value.lower(), str(value))
                        + "\n"
                    )
                else:
                    result += f"{value}\n"
            return result

        return "{\n" + pprint_dict(d) + "}"





    @staticmethod
    def wrap_styled_text(styled_text: str, width: int, tab_width: int = 8, pattern_key: str = None) -> List[str]:
        """
        Wraps the styled text (which includes ANSI codes) to the specified width.
        """
        pattern_dict = ansi_escape_patterns
        pattern = pattern_dict.get(pattern_key, pattern_dict['core'])

        i = 0
        line = ''
        lines = []
        line_length = 0

        while i < len(styled_text):
            if styled_text[i] == '\x1b':
                # Handle ANSI escape sequences
                m = pattern.match(styled_text, i)
                if m:
                    ansi_seq = m.group()
                    line += ansi_seq
                    i = m.end()
                else:
                    # Invalid ANSI code
                    line += styled_text[i]
                    i += 1
            else:
                # Handle visible character
                char = styled_text[i]
                if char == '\n':
                    # Newline, reset line length
                    line += char
                    lines.append(line)
                    line = ''
                    line_length = 0
                    i += 1
                elif char == '\t':
                    # Expand tab
                    spaces = tab_width - (line_length % tab_width)
                    line += ' ' * spaces
                    line_length += spaces
                    i += 1
                else:
                    # Regular character
                    w = 1  # Assuming monospaced font
                    if line_length + w > width:
                        # Need to wrap
                        lines.append(line)
                        line = ''
                        line_length = 0
                    line += char
                    line_length += w
                    i += 1
        if line:
            lines.append(line)
        return lines


    def get_visible_length(self, text, tab_width=None, ansi_pattern_key=None, contains_ansi=True):
        """
        Calculate the visible length of a single line.
        - Resets the length after each `\n`.
        - Expands `\t` to the next tab stop.
        """

        if not tab_width:
            tab_width = self.config.get('tab_width', 4)

        if contains_ansi:
            # Remove ANSI codes
            visible_text = PrintsCharming.remove_ansi_codes(text, pattern_key=ansi_pattern_key)
        else:
            visible_text = text

        length = 0
        for char in visible_text.expandtabs(tab_width):
            if char == '\n':
                length = 0  # Reset length after newline
            elif char == '\t':
                length += tab_width - (length % tab_width)  # Expand tab to next tab stop
            else:
                length += 1  # Count visible characters
        return length


    @staticmethod
    def replace_leading_newlines_tabs(s: str, fill_with: str, tab_width: int, pattern_key: str = None, contains_ansi=True) -> str:
        leading_ansi_codes = ''
        if contains_ansi:
            # Extract leading ANSI codes
            pattern_dict = ansi_escape_patterns
            pattern = pattern_dict.get(pattern_key, pattern_dict['core'])

            index = 0
            while index < len(s):
                if s[index] == '\x1b':
                    m = pattern.match(s, index)
                    if m:
                        ansi_seq = m.group()
                        leading_ansi_codes += ansi_seq
                        index = m.end()
                    else:
                        break
                else:
                    break
            s = s[index:]

        # Match leading newlines and tabs
        leading_ws_match = PrintsCharming.leading_ws_pattern.match(s)
        if leading_ws_match:
            leading_ws = leading_ws_match.group(1)
            n_newlines = leading_ws.count('\n')
            n_tabs = leading_ws.count('\t')
            fill_prefix = '\n' * n_newlines + fill_with * (tab_width * n_tabs)
            s = s[len(leading_ws):]
        else:
            fill_prefix = ''

        # Reconstruct the string
        s = leading_ansi_codes + fill_prefix + s
        return s



    def wrap_text_ansi_aware(
            self,
            text: str,
            width: int,
            indent: int = 0,
            tab_width: int = 4,
            max_lines: int = 0,
            fill_char: str = ' ',
            prepend_fill: Union[bool, int] = False,
            fill_to_end: Union[bool, int] = False,
            pattern_key: str = None,
            markdown: bool = False,
            preserve_newlines: bool = False  # <-- Our new toggle
    ) -> List[str]:
        """
        If preserve_newlines=True, do a line-by-line approach:
           - Keep every explicit newline exactly once,
           - but still wrap lines that exceed 'width'.

        Otherwise, use the old paragraph-based logic.
        """

        indent_str = ' ' * indent

        # ------------------------------------------------------------------------
        #  1) LINE-BY-LINE LOGIC (preserve_newlines = True)
        # ------------------------------------------------------------------------
        if preserve_newlines:
            lines_in = text.splitlines(True)  # each item may end with '\n'
            # If the first line is only ANSI + newline, discard it:
            if lines_in and not PrintsCharming.remove_ansi_codes(lines_in[0]).strip():
                lines_in.pop(0)
            #print(f'lines_in:')
            #print(repr(lines_in))
            #print(f'\n\n\n')
            wrapped_lines: List[str] = []

            for original_line in lines_in:
                # Check trailing newline
                has_trailing_newline = original_line.endswith('\n')
                # Strip it from the end so we can wrap cleanly
                line_no_nl = original_line.rstrip('\n')

                # If line_no_nl is blank (just whitespace or empty), preserve it
                if not PrintsCharming.remove_ansi_codes(line_no_nl.strip()):
                    # Might still want to do leading tab replacements if desired
                    if prepend_fill:
                        line_no_nl = self.replace_leading_newlines_tabs(
                            line_no_nl, fill_char, tab_width, pattern_key, contains_ansi=True
                        )
                    # Just append the blank line (no wrapping needed)
                    # If there was a trailing newline, we still want a single newline in the output
                    if has_trailing_newline:
                        wrapped_lines.append(line_no_nl + '\n')
                    else:
                        wrapped_lines.append(line_no_nl)
                    continue

                # Optional: leading whitespace replacement
                if prepend_fill:
                    line_no_nl = self.replace_leading_newlines_tabs(
                        line_no_nl, fill_char, tab_width,
                        pattern_key=pattern_key, contains_ansi=True
                    )

                current_line = indent_str
                current_len = self.get_visible_length(
                    current_line, tab_width=tab_width, ansi_pattern_key=pattern_key, contains_ansi=True
                )

                words = line_no_nl.split()
                lines_for_this_original = 0

                for word in words:
                    if not word:
                        continue
                    word_len = self.get_visible_length(
                        word, tab_width=tab_width, ansi_pattern_key=pattern_key, contains_ansi=True
                    )
                    spacer = 1 if current_line.strip() else 0

                    # If we exceed the width, push current_line and start a new line
                    if current_len + word_len + spacer > width:
                        if fill_to_end:
                            pad_amount = max(0, width - self.get_visible_length(current_line, tab_width))
                            current_line += fill_char * pad_amount

                        wrapped_lines.append(current_line)
                        current_line = indent_str + word
                        current_len = self.get_visible_length(
                            current_line, tab_width=tab_width,
                            ansi_pattern_key=pattern_key, contains_ansi=True
                        )

                        lines_for_this_original += 1
                        # Handle max_lines if given
                        if max_lines > 0 and lines_for_this_original >= max_lines:
                            if len(words) > 1:
                                # Add ellipsis
                                wrapped_lines[-1] = wrapped_lines[-1].rstrip('\n') + '...\n'
                            break
                    else:
                        # Add word to current line
                        current_line += (' ' if current_line.strip() else '') + word
                        current_len += word_len + spacer

                # Add the remainder of current_line (if any)
                if current_line.strip():
                    if fill_to_end:
                        pad_amount = max(0, width - self.get_visible_length(current_line, tab_width))
                        current_line += fill_char * pad_amount

                    # DO NOT forcibly add '\n' here in all cases
                    # We'll do that conditional logic below
                    wrapped_lines.append(current_line)
                else:
                    # If the line ended up empty, just preserve it
                    wrapped_lines.append(current_line)

                # If original line had a trailing newline,
                # ensure exactly one newline at the end of the last appended line
                if has_trailing_newline and wrapped_lines:
                    if not wrapped_lines[-1].endswith('\n'):
                        wrapped_lines[-1] += '\n'

            return wrapped_lines

        # ------------------------------------------------------------------------
        #  2) PARAGRAPH-BASED LOGIC (old approach)
        # ------------------------------------------------------------------------
        paragraphs = text.splitlines(keepends=True)
        wrapped_lines: List[str] = []

        for paragraph in paragraphs:
            has_trailing_newline = paragraph.endswith('\n')
            paragraph_no_nl = paragraph.rstrip('\n')

            # If blank paragraph => just preserve
            if not paragraph_no_nl.strip():
                # e.g. it's empty or only spaces
                wrapped_lines.append(paragraph)
                continue

            # Possibly do leading whitespace/tabs replacement
            if prepend_fill:
                paragraph_no_nl = self.replace_leading_newlines_tabs(
                    paragraph_no_nl, fill_char, tab_width,
                    pattern_key=pattern_key, contains_ansi=True
                )

            current_line = indent_str
            current_len = self.get_visible_length(
                current_line, tab_width=tab_width, ansi_pattern_key=pattern_key, contains_ansi=True
            )
            lines_this_paragraph = 0
            words = paragraph_no_nl.split()

            for word in words:
                if not word:
                    continue
                word_len = self.get_visible_length(
                    word, tab_width=tab_width, ansi_pattern_key=pattern_key, contains_ansi=True
                )
                spacer = 1 if current_line.strip() else 0

                if current_len + word_len + spacer > width:
                    if fill_to_end:
                        pad_amount = max(0, width - self.get_visible_length(current_line, tab_width))
                        current_line += fill_char * pad_amount

                    wrapped_lines.append(current_line)
                    current_line = indent_str + word
                    current_len = self.get_visible_length(
                        current_line, tab_width=tab_width, ansi_pattern_key=pattern_key, contains_ansi=True
                    )
                    lines_this_paragraph += 1

                    if max_lines > 0 and lines_this_paragraph >= max_lines:
                        if len(words) > 1:
                            wrapped_lines[-1] = wrapped_lines[-1].rstrip('\n') + '...\n'
                        break
                else:
                    current_line += (' ' if current_line.strip() else '') + word
                    current_len += word_len + spacer

            # Add the final line of this paragraph
            if current_line.strip():
                if fill_to_end:
                    pad_amount = max(0, width - self.get_visible_length(current_line, tab_width))
                    current_line += fill_char * pad_amount
                wrapped_lines.append(current_line)
            else:
                wrapped_lines.append(current_line)

            # Now reapply exactly one trailing newline if original paragraph had it
            if has_trailing_newline and wrapped_lines:
                if not wrapped_lines[-1].endswith('\n'):
                    wrapped_lines[-1] += '\n'

        return wrapped_lines


    @staticmethod
    def contains_ansi_codes(s: str) -> bool:
        """
        Checks if a string contains ANSI codes.

        :param s: The input string.
        :return: True if the string contains ANSI codes, False otherwise.
        """
        return '\x1b' in s


    @staticmethod
    def write_file(text: str, filename: str, end: str, mode: str = 'a') -> None:
        """
        Writes text to a file.

        :param text: The text to write.
        :param filename: The name of the file.
        :param end: The ending to append after the text.
        :param mode: The file opening mode.
        """
        with open(filename, mode) as file:
            file.write(text + end)


    @staticmethod
    def check_dict_structure(d: Dict[Any, Any]) -> str:
        """
        Checks the structure of a dictionary.

        :param d: The dictionary to check.
        :return: A string representing the detected structure ('indexed_style', 'splits', or 'Unknown structure').
        """
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
                        *args: Any,
                        converted_args: Optional[List[str]] = None,
                        sep: Union[str, Tuple[str, ...]] = ' ',
                        prog_sep: str = '',
                        prog_step: int = 1,
                        start: str = '',
                        prog_direction: str = 'forward'
                        ) -> str:
        """
        Formats text with separators and progression options.

        :param args: The arguments to format.
        :param converted_args: Pre-converted arguments if available.
        :param sep: Separator between arguments.
        :param prog_sep: Progressive separator to apply between arguments.
        :param prog_step: Step for the progressive separator.
        :param start: String to prepend to the final output.
        :param prog_direction: Direction of progression ('forward' or 'reverse').
        :return: The formatted text.
        """

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
    def get_words_and_spaces(text: str) -> List[str]:
        """
        Splits text into a list of words and spaces.

        :param text: The input text.
        :return: A list of words and spaces in order of appearance.
        """
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
              tab_width: int = None,
              container_width: int = None,
              ansi_pattern_key: str = None,
              prepend_fill: bool = False,
              fill_to_end: bool = False,
              fill_with: str = ' ',
              word_wrap: bool = True,
              filename: str = None,
              skip_ansi_check: bool = False,
              phrase_search: bool = True,
              phrase_norm: bool = False,
              phrase_norm_sep: str = ' ',
              word_search: bool = True,
              subword_search: bool = True,
              subword_style_option: int = 1,  # 1, 2, 3, 4, or 5 (see below)
              return_styled_text: bool = False,
              **kwargs: Any) -> None:



        converted_args = [str(arg) for arg in args] if self.config["args_to_strings"] else args
        self.debug(f'converted_args:\n{converted_args}')

        if not prog_sep:
            text = sep.join(converted_args)
        else:
            text = self.format_with_sep(converted_args=converted_args, sep=sep, prog_sep=prog_sep, prog_step=prog_step, prog_direction=prog_direction)

        self.debug(f"text defined:\n{text}")


        if self.contains_ansi_codes(start + text):
            text_without_ansi_codes = PrintsCharming.remove_ansi_codes(start + text)

            # Handle not colored text
            if not self.config["color_text"]:
                if filename:
                    self.write_file(text_without_ansi_codes, filename, end)
                else:
                    print(text_without_ansi_codes, end=end)
                return

            if not skip_ansi_check:
                if filename:
                    self.write_file(text, filename, end)
                else:
                    print(text, end=end)
                return
        else:
            text_without_ansi_codes = start + text


        if not tab_width:
            tab_width = self.config.get('tab_width', 4)

        if not container_width:
            container_width = self.terminal_width


        """
        # Check for ANSI codes in converted_args
        if not skip_ansi_check and any(self.contains_ansi_codes(arg) for arg in converted_args):
            if filename:
                self.write_file(text, filename, end)
            else:
                print(text, end=end)
            return
        """

        if isinstance(style, dict):
            dict_type = self.check_dict_structure(style)
            if dict_type == "indexed_style":
                text = self.style_words_by_index(text, style)
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
        # words_and_spaces = PrintsCharming.words_and_spaces_pattern.findall(text)
        words_and_spaces = self.get_words_and_spaces(start + text)

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

        # Handle trie_manager logic
        trie_manager = self.trie_manager
        if trie_manager:

            # Step 1: Handle phrases
            # Instance level check
            if trie_manager.enable_styled_phrases:
                # Method level check
                if phrase_search:
                    if len(words_and_spaces) >= trie_manager.shortest_phrase_length:
                        for i in range(len(words_and_spaces)):
                            # Build the text segment starting from the current position
                            text_segment = ''.join(words_and_spaces[i:])

                            # Search for the longest matching phrase in the phrase trie
                            phrase_match = trie_manager.phrase_trie.search_longest_prefix(text_segment, phrase_norm, phrase_norm_sep)
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
            if trie_manager.enable_styled_words:
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

                            if trie_manager.enable_word_trie:
                                # Check if the word is in the word trie
                                word_match = trie_manager.word_trie.search_longest_prefix(stripped_word)
                                self.debug(f'word_match: {word_match}')
                                if word_match:
                                    matched_word, word_details = word_match
                                    self.debug(f'word_match True:\nmatched_word: {matched_word}\nword_details: {word_details}')

                            elif trie_manager.enable_word_map:
                                word_details = trie_manager.word_map.get(stripped_word)


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
                                if trie_manager.enable_styled_subwords and subword_search:
                                    if isinstance(subword_style_option, int) and subword_style_option in range(1, 6):
                                        subword_match = False

                                        if subword_style_option == 1:
                                            # Use the specialized prefix search method
                                            prefix_match = trie_manager.subword_trie.search_prefix(stripped_word)
                                            if prefix_match:
                                                matched_substring, substring_details = prefix_match
                                                subword_match = True

                                        elif subword_style_option == 2:
                                            # Use the specialized suffix search method
                                            suffix_match = trie_manager.subword_trie.search_suffix(stripped_word)
                                            if suffix_match:
                                                matched_substring, substring_details = suffix_match
                                                subword_match = True

                                        elif subword_style_option == 3:
                                            # Earliest added match
                                            substring_matches = trie_manager.subword_trie.search_any_substring_by_insertion_order(stripped_word)
                                            if substring_matches:
                                                matched_substring, substring_details, _ = substring_matches[0]
                                                subword_match = True

                                        elif subword_style_option == 4:
                                            # Most recently added match
                                            substring_matches = trie_manager.subword_trie.search_any_substring_by_insertion_order(stripped_word)
                                            if substring_matches:
                                                matched_substring, substring_details, _ = substring_matches[-1]
                                                subword_match = True

                                        elif subword_style_option == 5:
                                            # Style only the matching substrings
                                            substring_matches = trie_manager.subword_trie.search_any_substring(stripped_word)
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

        self.debug(f"styled_text:\n{styled_text}")

        self.debug(f"styled_text_length:\n{len(styled_text)}")


        if fill_to_end or word_wrap or prepend_fill:
            if word_wrap:
                #wrapped_styled_lines = self.wrap_styled_text(styled_text, container_width, tab_width)
                wrapped_styled_lines = self.wrap_text_ansi_aware(styled_text, container_width, tab_width=tab_width)
            else:
                wrapped_styled_lines = styled_text.splitlines(keepends=True)

            final_lines = []
            for line in wrapped_styled_lines:
                # Handle prepend_fill
                if prepend_fill:
                    # Replace leading newlines and tabs in 'line' with fill_with * (tab_width * n_tabs)
                    line = self.replace_leading_newlines_tabs(line, fill_with, tab_width)

                # Calculate the number of trailing newlines
                trailing_newlines = len(line) - len(line.rstrip('\n'))

                # Check if the line is empty (contains only a newline character)
                stripped_line = line.rstrip('\n')
                has_newline = line.endswith('\n')

                if fill_to_end:
                    """
                    # Calculate the visible length of the line
                    visible_line = PrintsCharming.remove_ansi_codes(line)
                    current_length = self.get_visible_length(visible_line.expandtabs(tab_width), tab_width=tab_width)
                    chars_needed = max(0, container_width - current_length)

                    # If the line ends with the ANSI reset code, remove it temporarily
                    has_reset = line.endswith(self.reset)
                    if has_reset:
                        line = line[:-len(self.reset)]

                    # Add padding spaces and then the reset code if it was present
                    padded_line = line + fill_with * chars_needed
                    if has_reset:
                        padded_line += self.reset

                    final_lines.append(padded_line)
                    """
                    current_length = self.get_visible_length(stripped_line, tab_width=tab_width)
                    chars_needed = max(0, container_width - current_length)

                    # If the line ends with the ANSI reset code, remove it temporarily
                    has_reset = stripped_line.endswith(self.reset)
                    if has_reset:
                        stripped_line = stripped_line[:-len(self.reset)]

                    # Add padding characters and then the reset code if it was present
                    padded_line = stripped_line + fill_with * chars_needed
                    if has_reset:
                        padded_line += self.reset

                    # Re-append the newline character if it was present
                    if trailing_newlines > 0:
                        padded_line += '\n' * trailing_newlines

                    final_lines.append(padded_line)
                else:
                    final_lines.append(line)

            # Combine the lines into the final styled output
            if any(line.endswith('\n') for line in final_lines):
                # Lines already contain newline characters; avoid adding extra newlines
                final_all_styled_text = ''.join(final_lines)
            else:
                # Lines do not contain newlines; join them with '\n'
                final_all_styled_text = '\n'.join(final_lines)

            """
            # Combine the lines into the final styled output
            final_all_styled_text = ''.join(final_lines)
            """

        else:
            final_all_styled_text = styled_text

        if return_styled_text:
            return final_all_styled_text + end

        # Print or write to file
        if filename:
            with open(filename, 'a') as file:
                #file.write(all_text)
                file.write(final_all_styled_text + end)
        else:
            #sys.stdout.write(all_text)
            sys.stdout.write(final_all_styled_text + end)
            # print(start + styled_text, end=end)


    def compare_dicts(self, dict1: Dict[str, Any], dict2: Dict[str, Any], keys: List[str]) -> Dict[str, bool]:
        """
        Compares two dictionaries for specified keys.

        :param dict1: The first dictionary.
        :param dict2: The second dictionary.
        :param keys: A list of keys to compare.
        :return: A dictionary mapping each key to a boolean indicating equality.
        """
        dict2 = self.apply_reverse_effect(dict2)

        results = {}
        for key in keys:
            if key in ['color', 'bg_color']:
                results[key] = dict1.get(key) == dict2.get(key) and dict1.get(key) is not None
            else:
                results[key] = dict1.get(key) == dict2.get(key) and dict1.get(key) is True
        return results

    @staticmethod
    def apply_reverse_effect(style_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Reverses color and background color in a style dictionary if 'reversed' is set.

        :param style_dict: The style dictionary.
        :return: The modified style dictionary.
        """
        if style_dict.get('reversed'):
            style_dict['color'], style_dict['bg_color'] = (
                style_dict.get('bg_color'), style_dict.get('color')
            )
        return style_dict


    def print_variables(self, text: str, text_style: Optional[str] = None, **kwargs: Tuple[Any, str]) -> None:
        """
        Prints variables with styles applied to placeholders.

        :param text: The text template.
        :param text_style: Optional text style to apply.
        :param kwargs: Mapping of variable names to (value, style).
        """
        # Apply styles to each variable in kwargs
        for key, value in kwargs.items():
            variable, var_style = value
            styled_var = f"{self.style_codes[var_style]}{str(variable)}{self.reset}"
            kwargs[key] = styled_var

        # Replace placeholders with styled variables
        text = text.format(**kwargs)

        self.print(text, style=text_style, skip_ansi_check=True)


    def replace_and_style_placeholders(
        self,
        text: str,
        placeholders: Dict[str, Any],
        enable_label_style: bool = True,
        top_level_label: str = 'top_level_label',
        sub_level_label: str = 'sub_level_label',
        label_delimiter: str = ':',
        style_function: Optional[Callable[[str, Dict[str, Any]], str]] = None,
        **style_kwargs: Any
    ) -> str:
        """
        Replaces placeholders with values and applies styles.

        :param text: The text containing placeholders.
        :param placeholders: A dictionary of placeholder keys and their values.
        :param enable_label_style: Whether to style labels.
        :param top_level_label: The style name for top-level labels.
        :param sub_level_label: The style name for sub-level labels.
        :param label_delimiter: The delimiter for labels.
        :param style_function: A function to apply additional styles.
        :param style_kwargs: Additional keyword arguments for the style function.
        :return: The styled text.
        """
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


    def print_progress_bar(self, total_steps: int = 4, bar_symbol: str = ' ', bar_length: int = 40, color: str = 'vgreen') -> None:
        """
        Prints a progress bar.

        :param total_steps: Total number of steps in the progress bar.
        :param bar_symbol: The symbol to represent progress.
        :param bar_length: The total length of the progress bar.
        :param color: The color of the progress bar.
        """
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

        trie_manager = self.trie_manager
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

                if trie_manager.enable_word_trie:
                    # Check if the word is in the word trie
                    word_match = trie_manager.word_trie.search_longest_prefix(stripped_word)
                    self.debug(f'word_match: {word_match}')
                    if word_match:
                        matched_word, word_details = word_match
                        self.debug(f'word_match True:\nmatched_word: {matched_word}\nword_details: {word_details}')

                elif trie_manager.enable_word_map:
                    word_details = trie_manager.word_map.get(stripped_word)

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
                    if trie_manager.enable_styled_subwords and subword_search:
                        if isinstance(subword_style_option, int) and subword_style_option in range(1, 6):
                            subword_match = False

                            if subword_style_option == 1:
                                # Use the specialized prefix search method
                                prefix_match = trie_manager.subword_trie.search_prefix(stripped_word)
                                if prefix_match:
                                    matched_substring, substring_details = prefix_match
                                    subword_match = True

                            elif subword_style_option == 2:
                                # Use the specialized suffix search method
                                suffix_match = trie_manager.subword_trie.search_suffix(stripped_word)
                                if suffix_match:
                                    matched_substring, substring_details = suffix_match
                                    subword_match = True

                            elif subword_style_option == 3:
                                # Earliest added match
                                substring_matches = trie_manager.subword_trie.search_any_substring_by_insertion_order(stripped_word)
                                if substring_matches:
                                    matched_substring, substring_details, _ = substring_matches[0]
                                    subword_match = True

                            elif subword_style_option == 4:
                                # Most recently added match
                                substring_matches = trie_manager.subword_trie.search_any_substring_by_insertion_order(stripped_word)
                                if substring_matches:
                                    matched_substring, substring_details, _ = substring_matches[-1]
                                    subword_match = True

                            elif subword_style_option == 5:
                                # Style only the matching substrings
                                substring_matches = trie_manager.subword_trie.search_any_substring(stripped_word)
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

        trie_manager = self.trie_manager

        for i in range(len(words_and_spaces)):
            # Build the text segment starting from the current position
            text_segment = ''.join(words_and_spaces[i:])

            # Search for the longest matching phrase in the phrase trie
            phrase_match = trie_manager.phrase_trie.search_longest_prefix(text_segment, phrase_norm, phrase_norm_sep)
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

    def printnl(
        self,
        lines: int = 1,
        fill_with: str = ' ',
        style: str = 'default',
        color: Optional[str] = None,
        bg_color: Optional[str] = None,
        reverse: Optional[bool] = None,
        bold: Optional[bool] = None,
        dim: Optional[bool] = None,
        italic: Optional[bool] = None,
        underline: Optional[bool] = None,
        overline: Optional[bool] = None,
        strikethru: Optional[bool] = None,
        conceal: Optional[bool] = None,
        blink: Optional[bool] = None,
        container_width: Optional[Union[None, int]] = None,
    ) -> None:

        """
        Prints a newline-separated styled string using the `print` method.

        This method provides a simplified interface to the more comprehensive `print` method,
        focusing on styling and formatting the fill_with string. It is ideal
        for printing blank lines or styled right side padding
        with default or custom configurations.

        Args:
            lines (int): The number of lines to print. Default to 1.
            fill_with (str): The character used to fill empty space. Defaults to a single space (' ').
            style (str): The style to apply to the characters. Defaults to 'default'.
            color (Optional[str]): The foreground color of the characters. Defaults to None.
            bg_color (Optional[str]): The background color of the characters. Defaults to None.
            reverse (Optional[bool]): Whether to reverse the foreground and background colors. Defaults to None.
            bold (Optional[bool]): Whether to render the characters in bold. Defaults to None.
            dim (Optional[bool]): Whether to render the characters in dim (faint) mode. Defaults to None.
            italic (Optional[bool]): Whether to render the characters in italic. Defaults to None.
            underline (Optional[bool]): Whether to underline the characters. Defaults to None.
            overline (Optional[bool]): Whether to overline the characters. Defaults to None.
            strikethru (Optional[bool]): Whether to apply a strikethrough to the characters. Defaults to None.
            conceal (Optional[bool]): Whether to conceal the characters. Defaults to None.
            blink (Optional[bool]): Whether to render the characters with a blinking effect. Defaults to None.
            container_width(Optional[Union[None, int]]: width of the newline. Defaults to None.

        Returns:
            None: This method does not return a value. It outputs the styled characters to the terminal.

        Behavior:
            - Automatically determines whether to fill the line to the end (`fill_to_end`) based on the
              presence of certain params.
            - Delegates the printing functionality to the `print2` method.

        Example Usages:
            ```python
            obj.printnl()
            obj.printnl(fill_with='-', color='blue', bg_color='dgray', underline=True)
            ```
            First usage prints a newline respecting the instances default bg_color.
            Second usage prints a line of filled dashes with a blue foreground, dark gray bg_color, underlined.
        """

        # Determine if we need to fill the line based on styling and content
        should_fill = any([
            self.default_bg_color,  # Instance has a default background color
            style != 'default',  # A specific style is applied
            bg_color,  # A background color is specified
            (color and fill_with != ' ')  # There's a foreground color and fill character is not a space
        ])

        if fill_with != ' ':
            if not container_width:
                container_width = self.terminal_width
            #fill_with = (fill_with * container_width) / len(fill_with)
            fill_with = (fill_with * ((container_width // len(fill_with)) + 1))[:container_width]

        # Generate the styled line once
        styled_line = self.print2(
            fill_with,
            style=style,
            color=color,
            bg_color=bg_color,
            reverse=reverse,
            bold=bold,
            dim=dim,
            italic=italic,
            underline=underline,
            overline=overline,
            strikethru=strikethru,
            conceal=conceal,
            blink=blink,
            container_width=container_width,
            fill_to_end=should_fill,
            return_styled_args_list=True,  # Return the styled line instead of printing
        )[0]

        # Generate multiple lines by repeating the styled line
        output = (styled_line + "\n") * lines

        # Print the final output
        #sys.stdout.write(output)
        self.write(output)


        """
        self.print2(
            fill_with,
            style=style,
            color=color,
            bg_color=bg_color,
            reverse=reverse,
            bold=bold,
            dim=dim,
            italic=italic,
            underline=underline,
            overline=overline,
            strikethru=strikethru,
            conceal=conceal,
            blink=blink,
            fill_to_end=should_fill,
            container_width=min(container_width, self.terminal_width),
        )
        """


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
               tab_width: Union[None, int] = None,
               container_width: Union[None, int] = None,
               prepend_fill: bool = False,
               prepend_with: str = ' ',
               fill_to_end: bool = False,
               fill_with: str = ' ',
               word_wrap: bool = False,
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
               rtl: bool = False,
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
                    text = self.style_words_by_index(text, style)
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
            words_and_spaces = self.get_words_and_spaces(start + text)
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

            # Handle trie_manager logic
            trie_manager = self.trie_manager
            if trie_manager:

                # Step 1: Handle phrases
                # Instance level check
                if trie_manager.enable_styled_phrases:
                    # Method level check
                    if phrase_search:
                        # Only perform phrase lookup if there are multiple elements (implying a possible phrase)
                        if words_and_spaces_length >= trie_manager.shortest_phrase_length:
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
                if trie_manager.enable_styled_words:
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
                    print(f'styled word or space is None')
                    styled_words_and_spaces[i] = f"{style_code}{words_and_spaces[i]}{self.reset}"
                    indexes_used_by_none_styling.add(i)

            self.debug(f'After handle default styling:\nindexes_used_by_none_styling:\n{indexes_used_by_none_styling}')
            self.debug(f'styled_words_and_spaces:\n{styled_words_and_spaces}')

            # Step 5: Join the styled_words_and_spaces to form the final styled text
            styled_text = ''.join(filter(None, styled_words_and_spaces))

            self.debug(f"styled_text:\n{styled_text}")

            self.debug(f"styled_text_length:\n{len(styled_text)}")


            if any((fill_to_end, word_wrap, prepend_fill)):
                if not tab_width:
                    tab_width = self.config.get('tab_width', 8)

                if not container_width:
                    container_width = self.terminal_width

                if word_wrap:
                    # Use the new wrap_styled_text function
                    wrapped_styled_lines = self.wrap_styled_text(styled_text, container_width, tab_width)
                else:
                    wrapped_styled_lines = styled_text.splitlines(keepends=True)

                final_lines = []
                for line in wrapped_styled_lines:
                    # Handle prepend_fill
                    if prepend_fill:
                        # Replace leading newlines and tabs in 'line' with prepend_with * (tab_width * n_tabs)
                        line = self.replace_leading_newlines_tabs(line, prepend_with, tab_width)

                    # Calculate the number of trailing newlines
                    trailing_newlines = len(line) - len(line.rstrip('\n'))

                    # Check if the line is empty (contains only a newline character)
                    stripped_line = line.rstrip('\n')
                    has_newline = line.endswith('\n')

                    if fill_to_end:
                        # Calculate the visible length of the line
                        visible_line = PrintsCharming.remove_ansi_codes(stripped_line)
                        current_length = self.get_visible_length(visible_line.expandtabs(tab_width), tab_width=tab_width)
                        chars_needed = max(0, container_width - current_length)

                        # If the line ends with the ANSI reset code, remove it temporarily
                        has_reset = stripped_line.endswith(self.reset)
                        if has_reset:
                            stripped_line = stripped_line[:-len(self.reset)]

                        # Add padding characters and then the reset code if it was present
                        padded_line = stripped_line + fill_with * chars_needed
                        if has_reset:
                            padded_line += self.reset

                        # Re-append the newline character if it was present
                        if trailing_newlines > 0:
                            padded_line += '\n' * trailing_newlines

                        final_lines.append(padded_line)
                    else:
                        final_lines.append(line)

                # Combine the lines into the final styled output
                if any(line.endswith('\n') for line in final_lines):
                    # Lines already contain newline characters; avoid adding extra newlines
                    final_all_styled_text = ''.join(final_lines)
                else:
                    # Lines do not contain newlines; join them with '\n'
                    final_all_styled_text = '\n'.join(final_lines)

            else:
                final_all_styled_text = styled_text


            if return_styled_args_list:
                return [final_all_styled_text]


            # Print or write to file
            if filename:
                with open(filename, 'a') as file:
                    #file.write(start + styled_text + end)
                    file.write(final_all_styled_text + end)
            else:
                #sys.stdout.write(start + styled_text + end)
                sys.stdout.write(final_all_styled_text + end)

        else:
            num_args = len(converted_args)

            # Ensure all parameters are lists to handle individual styling for each arg
            def ensure_list(param, length):
                if param is None or isinstance(param, str) or isinstance(param, bool) or isinstance(param, dict):
                    return [param] * length  # Broadcast single value to all args
                return param

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
                        arg = self.style_words_by_index(arg, styles[i])
                    elif dict_type == 'splits':
                        arg = self.segment_and_style(arg, styles[i])
                    elif dict_type == 'splits_with_lists':
                        arg = self.segment_and_style2(arg, styles[i])


                #if isinstance(styles[i], dict):
                    #arg = self._style_words_by_index(arg, styles[i])



                # Convert the text to a list of words and spaces
                #words_and_spaces = PrintsCharming.words_and_spaces_pattern.findall(arg)
                if i == 0:
                    words_and_spaces = self.get_words_and_spaces(start + arg)
                else:
                    words_and_spaces = self.get_words_and_spaces(arg)

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

                # Handle trie_manager logic
                trie_manager = self.trie_manager
                if trie_manager:

                    # Step 1: Handle phrases
                    # Instance level check
                    if trie_manager.enable_styled_phrases:
                        # Method level check
                        if phrase_search:
                            if len(words_and_spaces) >= trie_manager.shortest_phrase_length:
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
                    if trie_manager.enable_styled_words:
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

            """
            if return_styled_args_list:
                return styled_parts
            """

            if not prog_sep:
                styled_parts_with_sep = sep.join(styled_parts)
            else:
                styled_parts_with_sep = self.format_with_sep(converted_args=styled_parts, sep=sep, prog_sep=prog_sep, prog_step=prog_step, prog_direction=prog_direction)

            self.debug(f"styled_parts_with_sep:\n{styled_parts_with_sep}")

            self.debug(f"styled_parts_with_sep_length:\n{len(styled_parts_with_sep)}")

            final_lines = None
            if fill_to_end or word_wrap or prepend_fill:
                if not tab_width:
                    tab_width = self.config.get('tab_width', 8)

                if not container_width:
                    container_width = self.terminal_width

                if word_wrap:
                    # Use the new wrap_styled_text function
                    wrapped_styled_lines = self.wrap_styled_text(styled_parts_with_sep, container_width, tab_width)
                else:
                    wrapped_styled_lines = styled_parts_with_sep.splitlines(keepends=True)

                final_lines = []
                for line in wrapped_styled_lines:
                    # Handle prepend_fill
                    if prepend_fill:
                        # Replace leading newlines and tabs in 'line' with fill_with * (tab_width * n_tabs)
                        line = self.replace_leading_newlines_tabs(line, prepend_with, tab_width)

                    # Calculate the number of trailing newlines
                    trailing_newlines = len(line) - len(line.rstrip('\n'))

                    # Check if the line is empty (contains only a newline character)
                    stripped_line = line.rstrip('\n')
                    has_newline = line.endswith('\n')

                    if fill_to_end:
                        # Calculate the visible length of the line
                        visible_line = PrintsCharming.remove_ansi_codes(stripped_line)
                        current_length = self.get_visible_length(visible_line.expandtabs(tab_width), tab_width=tab_width)
                        chars_needed = max(0, container_width - current_length)

                        # If the line ends with the ANSI reset code, remove it temporarily
                        has_reset = stripped_line.endswith(self.reset)
                        if has_reset:
                            stripped_line = stripped_line[:-len(self.reset)]

                        # Add padding characters and then the reset code if it was present
                        padded_line = stripped_line + fill_with * chars_needed
                        if has_reset:
                            padded_line += self.reset

                        # Re-append the newline character if it was present
                        if trailing_newlines > 0:
                            padded_line += '\n' * trailing_newlines

                        final_lines.append(padded_line)
                    else:
                        final_lines.append(line)

                # Combine the lines into the final styled output
                if any(line.endswith('\n') for line in final_lines):
                    # Lines already contain newline characters; avoid adding extra newlines
                    final_all_styled_text = ''.join(final_lines)
                else:
                    # Lines do not contain newlines; join them with '\n'
                    final_all_styled_text = '\n'.join(final_lines)

            else:
                final_all_styled_text = styled_parts_with_sep

            if return_styled_args_list:
                return final_lines or [styled_parts_with_sep]


            # Print or write to file
            if filename:
                with open(filename, 'a') as file:
                    file.write(final_all_styled_text + end)
            else:
                sys.stdout.write(final_all_styled_text + end)
                # print(start + styled_text, end=end)

            """
            # Print or write to file
            if filename:
                with open(filename, 'a') as file:
                    file.write(start + styled_parts_with_sep + end)
            else:
                sys.stdout.write(start + styled_parts_with_sep + end)
                # print(start + styled_text, end=end)
            """


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
        return self.segment_styler.segment_with_splitter_and_style(
            text,
            splitter_match,
            splitter_swap,
            splitter_show,
            splitter_style,
            splitter_arms,
            string_style
        )

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
        return self.segment_styler.segment_and_style2(text, styles_dict)


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
        return self.segment_styler.segment_and_style(text, styles_dict)

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
        return self.segment_styler.segment_and_style_update(text, styles_dict)

    # Special method called by the print method when style param is a dict
    # Does not style spaces only words
    def _style_words_by_index(self,
                              text: str, style: Dict[Union[int, Tuple[int, int]], str]
                              ) -> str:
        """
        Styles words in the text based on their index or a range of indices.

        :param text: The input text to style.
        :param style: A dictionary mapping indices or index ranges to style names.
        :return: The styled text.
        """
        return self.segment_styler._style_words_by_index(text, style)

    # Public facing method that accounts for whitespace and styles it and words.
    def style_words_by_index(self, text: str, style: Dict[Union[int, Tuple[int, int]], str]) -> str:
        """
        Styles words and whitespace in the text based on their index or a range of indices.

        :param text: The input text to style.
        :param style: A dictionary mapping indices or index ranges to style names.
        :return: The styled text.
        """
        return self.segment_styler.style_words_by_index(text, style)




    # This is for internal logging within this class!!!
    def setup_internal_logging(self, log_level: str, log_format: str = '%(message)s') -> None:
        """
        Sets up internal logging.

        :param log_level: Logging level (e.g., 'DEBUG', 'INFO').
        :param log_format: Logging format.
        """
        # Configure the shared logger's level
        self.logger.setLevel(getattr(logging, log_level.upper(), logging.DEBUG))

        # Logging is controlled by the instance, not by disabling the logger itself
        if self.internal_logging_enabled:
            self.info("Internal Logging Enabled for this instance.")
            logging_enabled_init_message = f"Instance config dict:\n{self.format_dict(self.config)}"
            self.debug(logging_enabled_init_message)


    def _apply_style_internal(self, style_name: str, text: Any, reset: bool = True) -> str:
        """
        Applies a style internally without logging debug messages.

        :param style_name: The name of the style to apply.
        :param text: The text to style.
        :param reset: Whether to reset styles after the text.
        :return: The styled text.
        """
        text = str(text)
        if isinstance(text, str) and text.isspace():
            style_code = self.bg_color_map.get(
                style_name,
                self.bg_color_map.get(
                    self.styles.get(style_name, PStyle(bg_color="default_bg")).bg_color
                )
            )
        else:
            style_code = self.style_codes.get(style_name, self.color_map.get(style_name, self.color_map.get('default')))

        # Append the style code at the beginning of the text and the reset code at the end
        styled_text = f"{style_code}{text}{self.reset if reset else ''}"

        return styled_text

    def log(self, level: str, message: str, *args: Any, **kwargs: Any) -> None:
        """
        Logs a message with styling.

        :param level: The log level (e.g., 'DEBUG', 'INFO').
        :param message: The message to log.
        :param args: Positional arguments for message formatting.
        :param kwargs: Keyword arguments for message formatting.
        """
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

    def debug(self, message: str, *args: Any, **kwargs: Any) -> None:
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

    def info(self, message: str, *args: Any, **kwargs: Any) -> None:
        self.log('INFO', message, *args, **kwargs)

    def warning(self, message: str, *args: Any, **kwargs: Any) -> None:
        self.log('WARNING', message, *args, **kwargs)

    def error(self, message: str, *args: Any, **kwargs: Any) -> None:
        self.log('ERROR', message, *args, **kwargs)

    def critical(self, message: str, *args: Any, **kwargs: Any) -> None:
        self.log('CRITICAL', message, *args, **kwargs)


def get_default_printer() -> Any:
    p = PrintsCharming()
    return p.print





