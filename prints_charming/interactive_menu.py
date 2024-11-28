# interactive_menu.py

import time
import sys
import json

from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from .prints_charming_defaults import (
    DEFAULT_CONFIG,
    DEFAULT_COLOR_MAP,
    DEFAULT_EFFECT_MAP,
    DEFAULT_STYLES,
    DEFAULT_LOGGING_STYLES
)

from .prints_charming import PrintsCharming

from .prints_style import PStyle

from .utils import get_key


class InteractiveMenu:
    _shared_instance = {}

    @classmethod
    def get_shared_instance(cls, key):
        """
        Get a shared instance of InteractiveMenu.

        Returns:
            InteractiveMenu: A shared InteractiveMenu instance or None if not set.
        """
        return cls._shared_instance.get(key)


    @classmethod
    def set_shared_instance(cls, instance, key):
        """
        Set a shared InteractiveMenu instance.

        Args:
            instance (InteractiveMenu): An InteractiveMenu instance to set as shared.
            key (str): The dictionary key used to store the shared instance.
        """
        cls._shared_instance[key] = instance


    def __init__(self, *initial_menu_configs, pc=None,
                 selected_style=None,
                 unselected_style=None,
                 confirmed_style=None,
                 alt_buffer=True,
                 menu_start_row=10,
                 ):

        if isinstance(pc, str):
            self.pc = PrintsCharming.get_shared_instance(pc)
            if not self.pc:
                self.pc = PrintsCharming()
                self.pc.warning(f"No shared instance found for key '{pc}'. Using a new instance with default init.")
        else:
            self.pc = pc or PrintsCharming()

        self.reset = self.pc.reset
        self.apply_style = self.pc.apply_style

        self.ctl = self.pc.ctl_map
        self.unicode = self.pc.unicode_map
        self.write = self.pc.write

        # Dictionary to hold menus and their types (vertical or horizontal)
        self.menus = {}
        self.menu_types = {}  # Stores whether each menu is 'hor' or 'vert'
        self.current_menu = None
        self.menu_stack = []  # To track the stack of menus for navigating back

        # Initialize the menus if any configurations are provided
        if initial_menu_configs:
            self._initialize_menus(initial_menu_configs)

        self.selected_style = selected_style
        self.unselected_style = unselected_style or 'default'
        self.confirmed_style = confirmed_style or selected_style

        self.selected_index = 0  # Vertical navigation index (styles)
        self.horizontal_index = 0  # Horizontal navigation index (attributes)

        self.alt_buffer = alt_buffer
        self.menu_start_row = menu_start_row

        self.get_key = get_key

        self.arrows = {
            'down': self.pc.apply_style(style_name='down_arrow', text="⭣"),
            'up': self.pc.apply_style(style_name='up_arrow', text="⭡"),
            'left': self.pc.apply_style(style_name='left_arrow', text="⇐"),
            'right': self.pc.apply_style(style_name='right_arrow', text="⇒")
        }

        self.vert_nav_directions = f" 'j' or {self.arrows.get('down')} to move down, 'k' or {self.arrows.get('up')} to move up.\n"
        self.hor_nav_directions = f" 'l' or {self.arrows.get('right')} to move right, 'h' or {self.arrows.get('left')} to move left.\n"




    def _initialize_menus(self, menu_configs):
        """Helper function to initialize menus from given configurations."""
        for config in menu_configs:
            if len(config) < 3:
                print(f"Invalid menu configuration: {config}")
                continue
            menu_name, menu_type, *options = config
            self.create_menu(menu_name, menu_type, options)


    def create_menu(self, menu_name, menu_type, options):
        """Create a new menu with a given name, type ('hor', 'vert', or 'nested'), and list of options or submenus."""
        if menu_type not in ['hor', 'vert', 'nested']:
            print(f"Invalid menu type '{menu_type}' for menu '{menu_name}'. Must be 'hor', 'vert', or 'nested'.")
            return
        self.menus[menu_name] = options
        self.menu_types[menu_name] = menu_type
        if not self.current_menu:
            self.current_menu = menu_name  # Set the current menu if none is set


    def switch_menu(self, menu_name):
        """Switch to a different menu by name."""
        if menu_name in self.menus:
            self.menu_stack.append(self.current_menu)  # Save current menu to stack for back navigation
            self.current_menu = menu_name
            self.selected_index = 0  # Reset navigation index when switching menus
        else:
            print(f"Menu '{menu_name}' does not exist.")


    def go_back(self):
        """Go back to the previous menu in the stack."""
        if self.menu_stack:
            self.current_menu = self.menu_stack.pop()
            self.selected_index = 0
        else:
            print("No previous menu to return to.")



    def display_highlighted_menu(self):
        """Displays the options for the current menu with the selected one highlighted."""
        if self.current_menu is None:
            print("No menu is currently active.")
            return

        self.write('cursor_position', row=self.menu_start_row, col=1)
        menu_options = self.menus[self.current_menu]  # Access options for the current menu
        menu_type = self.menu_types[self.current_menu]  # Get whether it's 'vert' or 'hor'

        for i, option in enumerate(menu_options):
            if isinstance(option, dict):
                option = list(option.keys())[0]  # If it's a nested menu, show the submenu name
            style = self.selected_style if i == self.selected_index else self.unselected_style
            display_text = f"({i + 1}) {option}" if menu_type == 'vert' else f"{option}  "
            self.pc.print(display_text, style=style)


    def navigate(self, direction):
        """Navigate through the current menu options."""
        if self.current_menu is None:
            print("No menu is currently active.")
            return

        menu_options = self.menus[self.current_menu]
        menu_type = self.menu_types[self.current_menu]

        # For vertical menus, navigate by changing the selected_index
        if menu_type == 'vert':
            self.selected_index = (self.selected_index + direction) % len(menu_options)
        # For horizontal menus, navigate horizontally
        elif menu_type == 'hor':
            self.selected_index = (self.selected_index + direction) % len(menu_options)

        # Handle nested menus (if the option is a dictionary representing a submenu)
        if isinstance(menu_options[self.selected_index], dict):
            submenu_name = list(menu_options[self.selected_index].keys())[0]
            self.switch_menu(submenu_name)

        # Clear and redisplay the menu
        for i in range(len(menu_options)):
            self.write('cursor_position', row=self.menu_start_row + i, col=1)

        self.display_highlighted_menu()


    def run(self):
        if self.alt_buffer:
            self.write('alt_buffer', 'cursor_home', 'hide_cursor')

        if self.current_menu is None:
            print("No menu is currently active.")
            return

        # Display instructions
        self.write(f"{self.pc.apply_style(style_name='vgreen', text='Please select an option:')}\n\n")
        self.write(self.vert_nav_directions if self.menu_types[self.current_menu] == 'vert' else self.hor_nav_directions)
        self.pc.print(f"\n  'q' to quit.\n\n", style="vred")

        self.display_highlighted_menu()

        confirmed_option = None

        while True:
            # Clear the input line before capturing the next input
            self.write('cursor_position', row=self.menu_start_row + len(self.menus[self.current_menu]) + 1, col=1)
            self.write('clear_line')  # Clear the current input line

            key = get_key()

            if key == 'q':
                break

            elif key in ['k', 'h', self.pc.ctl_map['arrow_up'], self.pc.ctl_map['arrow_left']]:
                self.navigate(-1)

            elif key in ['j', 'l', self.pc.ctl_map['arrow_down'], self.pc.ctl_map['arrow_right']]:
                self.navigate(1)

            elif key == '\r':
                confirmed_option = self.menus[self.current_menu][self.selected_index]
                break

        if self.alt_buffer:
            self.write('normal_buffer', 'show_cursor')

        self.pc.print(f'confirmed_option: {confirmed_option}', style={1: self.confirmed_style, (2, 3): self.selected_style})

        return self.selected_index + 1



"""
class InteractiveMenu:
    def __init__(self, options, pc=None, styles=None, key_bindings=None, state=None, config=None):
        self.styles = styles or {
            'selected': PrintsStyle(color='vcyan'),
            'unselected': PrintsStyle(),
            'confirmed': PrintsStyle(color='vgreen'),
            'multi_selected': PrintsStyle(color='vyellow')
        }
        self.pc = pc or PrintsCharming()
        self.control_map = self.pc.CONTROL_MAP  # Use control map from PrintsCharming instance
        self.options = options

        self.key_bindings = key_bindings or {}
        self.state = state or {
            'selected_index': 0,
            'selected_items': set(),  # For multi-selection
            'search_query': "",
        }
        self.config = config or {
            'multi_select': False,
            'editable': False,
            'searchable': False,
            'hierarchical': False,
            'scrollable': False,
            'confirm_required': False,
        }

    def display_menu(self):
        start_index, end_index = self.get_scroll_indices()
        for i, option in enumerate(self.options[start_index:end_index]):
            global_index = i + start_index
            style = self.determine_style(global_index)
            self.pc.print(f"{global_index + 1}. {option}", style=style)

    def get_scroll_indices(self):
        if not self.config['scrollable']:
            return 0, len(self.options)
        max_display = 10  # Example: Display 10 items at a time
        start_index = max(0, self.state['selected_index'] - max_display // 2)
        end_index = min(len(self.options), start_index + max_display)
        return start_index, end_index

    def determine_style(self, global_index):
        if global_index == self.state['selected_index']:
            return self.styles['selected']
        elif global_index in self.state['selected_items']:
            return self.styles['multi_selected']
        else:
            return self.styles['unselected']

    def run(self):
        raise NotImplementedError("Subclasses should implement this method to provide specific behavior.")

"""