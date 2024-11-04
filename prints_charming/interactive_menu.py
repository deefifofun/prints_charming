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
    _shared_pc_instance = None

    @classmethod
    def get_shared_pc_instance(cls):
        """
        Get the shared PrintsCharming instance for InteractiveMenu.

        Returns:
            PrintsCharming: The shared PrintsCharming instance for InteractiveMenu, or None if not set.
        """
        return cls._shared_pc_instance

    @classmethod
    def set_shared_pc_instance(cls, pc_instance):
        """
        Set the shared PrintsCharming instance for InteractiveMenu.

        Args:
            pc_instance (PrintsCharming): The PrintsCharming instance to set as shared for InteractiveMenu.
        """
        cls._shared_pc_instance = pc_instance

    def __init__(self, selected_style, *initial_menu_configs, pc=None,
                 unselected_style=None,
                 confirmed_style=None,
                 alt_buffer=False,
                 menu_start_row=10,
                 styles_file='styles.json'
                 ):


        self.pc = (
                pc
                or self.__class__.get_shared_pc_instance()
                or PrintsCharming.get_shared_instance()
                or PrintsCharming()
        )
        self.reset = self.pc.reset

        # Dictionary to hold menus and their types (vertical or horizontal)
        self.menus = {}
        self.menu_types = {}  # Stores whether each menu is 'hor' or 'vert'
        self.current_menu = None
        self.menu_stack = []  # To track the stack of menus for navigating back

        # Initialize the menus if any configurations are provided
        if initial_menu_configs:
            self._initialize_menus(initial_menu_configs)

        self.ctl_map = self.pc.ctl_map
        self.apply_style = self.pc.apply_style
        self.selected_style = selected_style
        self.unselected_style = unselected_style or 'default'
        self.confirmed_style = confirmed_style or selected_style
        self.selected_index = 0  # Vertical navigation index (styles)
        self.horizontal_index = 0  # Horizontal navigation index (attributes)
        self.alt_buffer = alt_buffer
        self.menu_start_row = menu_start_row
        self.arrows = {
            'down': self.pc.apply_style(style_name='down_arrow', text="⭣"),
            'up': self.pc.apply_style(style_name='up_arrow', text="⭡"),
            'left': self.pc.apply_style(style_name='left_arrow', text="⇐"),
            'right': self.pc.apply_style(style_name='right_arrow', text="⇒")
        }

        self.vert_nav_directions = f" 'j' or {self.arrows.get('down')} to move down, 'k' or {self.arrows.get('up')} to move up.\n"
        self.hor_nav_directions = f" 'l' or {self.arrows.get('right')} to move right, 'h' or {self.arrows.get('left')} to move left.\n"

        self.edit_mode = False  # To enter edit mode for color/bg_color
        self.current_style_name = None

        self.styles_to_edit = None
        self.style_names_to_edit = None
        self.colors = None

        self.styles_file = styles_file  # File to save/load styles
        self.loaded_style_set = None  # Track which style set is loaded




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
            self.write('alt_buffer', 'cursor_home')

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

            elif key in ['k', 'h', self.ctl_map['arrow_up'], self.ctl_map['arrow_left']]:
                self.navigate(-1)

            elif key in ['j', 'l', self.ctl_map['arrow_down'], self.ctl_map['arrow_right']]:
                self.navigate(1)

            elif key == '\r':
                confirmed_option = self.menus[self.current_menu][self.selected_index]
                break

        if self.alt_buffer:
            self.write('normal_buffer')

        self.pc.print(f'confirmed_option: {confirmed_option}', style={1: self.confirmed_style, (2, 3): self.selected_style})

        return self.selected_index + 1




    def load_styles(self):
        """Load multiple style dictionaries from the JSON file."""
        try:
            with open(self.styles_file, 'r') as f:
                style_sets = json.load(f)
                if style_sets:
                    print("Available style dictionaries:")
                    for name in style_sets.keys():
                        print(f"- {name}")
                    selected_set = input("Enter the name of the style dictionary to load (or press Enter to skip): ").strip()
                    if selected_set in style_sets:
                        self.styles = {k: PStyle(**v) for k, v in style_sets[selected_set].items()}
                        self.style_names = list(self.styles.keys())
                        self.loaded_style_set = selected_set
                        print(f"Loaded style set '{selected_set}' from {self.styles_file}")
                    else:
                        print("No valid selection made. Starting with a blank slate.")
        except FileNotFoundError:
            print(f"No existing styles found. Starting with a blank slate.")



    def save_styles(self):
        """Save the current styles dictionary to the JSON file under a specific name."""
        style_set_name = input(f"Enter a name for this style set (current: {self.loaded_style_set or 'unnamed'}): ").strip()
        if not style_set_name:
            print("Save aborted. Style set name cannot be empty.")
            return

        # Load the existing style sets from the file, if any
        try:
            with open(self.styles_file, 'r') as f:
                style_sets = json.load(f)
        except FileNotFoundError:
            style_sets = {}

        # Save the current styles under the given name
        style_sets[style_set_name] = {k: v.__dict__ for k, v in self.styles.items()}

        with open(self.styles_file, 'w') as f:
            json.dump(style_sets, f, indent=4)

        self.loaded_style_set = style_set_name
        print(f"Styles saved under '{style_set_name}' in {self.styles_file}")



    def load_style_editor(self, colors, styles=None):
        self.styles_to_edit = styles if styles else {
            "default": PStyle()
        }
        self.style_names_to_edit = list(self.styles_to_edit.keys())
        self.colors = colors
        self.display_styles_editor()



    def create_new_style(self):
        """Create a new style interactively."""
        print("Press 'n' to create a new style.")
        user_input = input().strip().lower()
        if user_input == 'n':
            style_name = input("Enter new style name: ")
            self.current_style_name = style_name
            new_style = PStyle()  # Start with a blank style template
            self.styles_to_edit[style_name] = new_style
            self.style_names_to_edit = list(self.styles_to_edit.keys())
            self.selected_index = len(self.style_names_to_edit) - 1  # Move to the newly created style

            # Display the style in edit mode
            self.edit_style(style_name)



    def edit_style(self, style_name):
        """Display and edit the style attributes interactively."""
        style = self.styles_to_edit[style_name]
        attributes = ['style_name', 'color', 'bg_color', 'bold', 'italic', 'underline', 'reverse', 'dim', 'overline', 'strikethru', 'conceal', 'blink']

        # Start with the `color` attribute selected
        self.horizontal_index = 1  # Start at 'color'
        self.edit_mode = True

        while self.edit_mode:
            # Display the style and its attributes
            self.display_style(style_name, style)

            # Allow navigation and editing
            key = get_key()

            if key in ['k', self.ctl_map['arrow_up']]:
                self.horizontal_index = max(0, self.horizontal_index - 1)  # Navigate upwards
            elif key in ['j', self.ctl_map['arrow_down']]:
                self.horizontal_index = min(len(attributes) - 1, self.horizontal_index + 1)  # Navigate downwards
            elif key == '\r':  # Enter key to edit the selected attribute
                self.edit_attribute(style, attributes[self.horizontal_index])
            elif key == 'q':  # Finish editing
                self.edit_mode = False


    def display_style(self, style_name, style):
        """Display the current style and its attributes."""
        self.write('cursor_position', row=self.menu_start_row, col=1)
        attr_list = [
            f"style_name={style_name}",
            f"color={style.color}",
            f"bg_color={style.bg_color}",
            f"bold={style.bold}",
            f"italic={style.italic}",
            f"underline={style.underline}",
            f"reverse={style.reverse}",
            f"dim={style.dim}",
            f"overline={style.overline}",
            f"strikethru={style.strikethru}",
            f"conceal={style.conceal}",
            f"blink={style.blink}"
        ]
        for i, attr in enumerate(attr_list):
            style_to_use = self.selected_style if i == self.horizontal_index else self.unselected_style
            self.pc.print(attr, style=style_to_use)



    def edit_attribute(self, style, attr_name):
        """Edit the currently selected attribute."""
        if attr_name == 'style_name':
            new_name = input(f"Enter new style name (current: {self.current_style_name}): ")
            if new_name.strip():
                # Rename the style
                self.styles_to_edit[new_name] = self.styles_to_edit.pop(self.current_style_name)
                self.current_style_name = new_name
                self.style_names_to_edit = list(self.styles_to_edit.keys())
        elif attr_name in ['color', 'bg_color']:
            new_value = input(f"Enter new value for {attr_name} (current: {getattr(style, attr_name)}): ")
            setattr(style, attr_name, new_value)
        else:
            # Toggle boolean attributes
            setattr(style, attr_name, not getattr(style, attr_name))



    def run_styles_editor(self):
        if self.alt_buffer:
            self.write('alt_buffer', 'cursor_home')

            # Display instructions
        self.write(f"{self.apply_style(style_name='vgreen', text='Navigate: j/k | Edit: Enter | Quit: q')}\n")
        self.display_styles_editor()

        while True:
            key = get_key()

            if key == 'q':
                break
            elif key == 'n':  # Start creating a new style
                self.create_new_style()
            elif key == 's':  # Save styles to file
                self.save_styles()

        if self.alt_buffer:
            self.write('normal_buffer')



    def display_styles_editor(self):
        """Displays the available styles."""
        self.write('cursor_position', row=self.menu_start_row, col=1)
        for i, style_name in enumerate(self.style_names_to_edit):
            style = self.styles_to_edit[style_name]

            true_color_code = self.pc.get_color_code('vgreen')
            false_color_code = self.pc.get_color_code('vred')

            color_code = self.colors.get(style.color, '')
            bg_code = color_code.replace('[38', '[48')

            bold_color_code = true_color_code if style.bold else false_color_code
            bold_code = bold_color_code + self.pc.effect_map.get('bold')

            italic_color_code = true_color_code if style.italic else false_color_code
            italic_code = italic_color_code + self.pc.effect_map.get('italic')

            ul_color_code = true_color_code if style.underline else false_color_code
            ul_code = ul_color_code + self.pc.effect_map.get('underline')

            reverse_code_combo = color_code + bg_code + self.pc.get_effect_code('reverse')
            reverse_code = reverse_code_combo if style.reverse else false_color_code

            dim_color_code = true_color_code if style.dim else false_color_code
            dim_code = dim_color_code + self.pc.effect_map.get('dim')

            ol_color_code = true_color_code if style.overline else false_color_code
            ol_code = ol_color_code + self.pc.effect_map.get('overline')

            st_color_code = true_color_code if style.strikethru else false_color_code
            st_code = st_color_code + self.pc.effect_map.get('strikethru')

            conceal_code = true_color_code if style.conceal else false_color_code

            bl_color_code = true_color_code if style.blink else false_color_code
            bl_code = bl_color_code + self.pc.effect_map.get('blink')



            attr_list = [
                f"color={color_code}{style.color}{self.reset}",
                f"bg_color={color_code}{bg_code}{style.bg_color}{self.reset}",
                f"bold={bold_code}{style.bold}{self.reset}",
                f"italic={italic_code}{style.italic}{self.reset}",
                f"underline={ul_code}{style.underline}{self.reset}",
                f"reverse={reverse_code}{style.reverse}{self.reset}",
                f"dim={dim_code}{style.dim}{self.reset}",
                f"overline={ol_code}{style.overline}{self.reset}",
                f"strikethru={st_code}{style.strikethru}{self.reset}",
                f"conceal={conceal_code}{style.conceal}{self.reset}",
                f"blink={bl_code}{style.blink}{self.reset}"
            ]
            style_line = f"{style_name}: {' | '.join(attr_list)}"
            display_style = self.selected_style if i == self.selected_index else self.unselected_style
            print(style_line)



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