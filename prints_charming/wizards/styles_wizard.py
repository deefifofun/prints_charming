import os
import re
import sys
import time
import random
import json
import argparse
import textwrap
import importlib.util
from dataclasses import asdict

if not sys.platform == 'win32':
    import readline

from prints_charming import (
    PStyle,
    PrintsCharming,
    InteractiveMenu,
    TableManager,
    BoundCell,
)











class StylesEditor:
    def __init__(self, menu_instance, styles_file='styles.json'):
        self.menu = menu_instance
        self.styles_file = styles_file
        self.styles = {}
        self.style_names = []
        self.edit_mode = False
        self.current_style_name = None
        self.styles_to_edit = {}
        self.style_names_to_edit = []
        self.colors = {}
        self.loaded_style_set = None



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
                        print(f"Successfully loaded style set '{selected_set}' from {self.styles_file}")
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


    def print_available_colors(self):
        """Display a list of available colors."""
        print("\nAvailable Colors (from color_map):\n")
        for name, code in self.colors.items():
            print(f"{code}{name}{reset}", end=" ")
        print("\n\n")



    def load_style_editor(self, colors, styles=None):
        """Initialize the styles editor with optional preloaded styles."""
        self.styles_to_edit = styles if styles else {
            "default": PStyle()
        }
        self.style_names_to_edit = list(self.styles_to_edit.keys())
        self.colors = colors
        self.display_styles_editor()



    def create_new_style(self):
        """Create a new style interactively."""
        print("To create a new style, press 'n'.")
        user_input = input().strip().lower()
        if user_input == 'n':
            style_name = input("Enter new style name: ")
            self.current_style_name = style_name
            new_style = PStyle()  # Start with a blank style template
            self.styles_to_edit[style_name] = new_style
            self.style_names_to_edit = list(self.styles_to_edit.keys())
            self.menu.selected_index = len(self.style_names_to_edit) - 1  # Move to the newly created style

            return style_name



    def edit_style(self, style_name):
        """Display and edit the style attributes interactively."""
        style = self.styles_to_edit[style_name]
        attributes = ['style_name', 'color', 'bg_color', 'bold', 'italic', 'underline', 'reverse', 'dim', 'overline', 'strikethru', 'conceal', 'blink']

        # Start with the `color` attribute selected
        self.menu.horizontal_index = 1  # Start at 'color'
        self.edit_mode = True

        while self.edit_mode:
            # Display the style and its attributes
            self.display_style(style_name, style)

            # Allow navigation and editing
            key = self.menu.get_key()

            if key in ['k', pc.ctl_map['arrow_up']]:
                self.menu.horizontal_index = max(0, self.menu.horizontal_index - 1)  # Navigate upwards
            elif key in ['j', pc.ctl_map['arrow_down']]:
                self.menu.horizontal_index = min(len(attributes) - 1, self.menu.horizontal_index + 1)  # Navigate downwards
            elif key == '\r':  # Enter key to edit the selected attribute
                self.edit_attribute(style, attributes[self.menu.horizontal_index])
            elif key == 'q':  # Finish editing
                self.edit_mode = False


    def display_defined_styles(self):
        """Display all defined styles in a readable format."""
        print("\nCurrently Defined Styles:")
        for style_name, style in self.styles_to_edit.items():
            attributes = [
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
            print(f"{style_name}: " + " | ".join(attributes))
        print()  # Add an extra line for readability


    def display_style(self, style_name, style):
        """Display the current style and its attributes."""
        pc.write('cursor_position', row=self.menu.menu_start_row, col=1)
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
            style_to_use = self.menu.selected_style if i == self.menu.horizontal_index else self.menu.unselected_style
            pc.print(attr, style=style_to_use)



    def edit_attribute(self, style, attr_name):
        """Edit the currently selected attribute."""
        if attr_name == 'style_name':
            pc.write("clear_screen")
            self.display_defined_styles()  # Show defined styles at the top
            new_name = input(f"Enter new style name (current: {self.current_style_name}, press Enter to keep): ")
            if new_name.strip():
                # Rename the style
                self.styles_to_edit[new_name] = self.styles_to_edit.pop(self.current_style_name)
                self.current_style_name = new_name
                self.style_names_to_edit = list(self.styles_to_edit.keys())
        elif attr_name in ['color', 'bg_color']:
            while True:
                pc.write("clear_screen")
                self.display_defined_styles()
                color = input(f"Enter new {attr_name} (current: {getattr(style, attr_name)}, type 'list' for available colors, press Enter to keep current): ").strip()
                if color.lower() == 'list':
                    self.print_available_colors()  # Show available colors if 'list' is entered
                elif color == "":  # Pressing Enter without input keeps the current value
                    print(f"{attr_name.capitalize()} remains as '{getattr(style, attr_name)}'.")
                    break
                elif color in self.colors:
                    setattr(style, attr_name, color)
                    print(f"{attr_name.capitalize()} changed to '{color}'.")
                    break
                else:
                    print("Invalid color. Please try again or type 'list' to see available colors.")
                    input("Press Enter to continue...")  # Pause before clearing to show error message

            """
            color_prompt = input(f"Enter new {attr_name} (current: {getattr(style, attr_name)}, type 'list' for available colors): ")
            if color_prompt.lower() == 'list':
                self.print_available_colors()
                color_prompt = input(f"Enter new {attr_name}: ")
            setattr(style, attr_name, color_prompt if color_prompt in self.colors else None)
            """

        else:
            # Toggle boolean attributes
            pc.write("clear_screen")
            self.print_available_colors()  # Show available colors
            self.display_defined_styles()  # Show defined styles
            setattr(style, attr_name, not getattr(style, attr_name))



    def run_styles_editor(self):
        """Run the interactive style editor, displaying instructions."""
        if self.menu.alt_buffer:
            pc.write('alt_buffer', 'clear_screen', 'cursor_home')

        # Display controls and instructions
        pc.write(f"{pc.apply_style(style_name='vgreen', text='Instructions: Navigate: j/k | Edit: Enter | New: n | Save: s | Quit: q')}\n\n")
        self.print_available_colors()
        self.display_styles_editor()

        while True:
            key = self.menu.get_key()

            if key == 'q':
                print("Exiting the styles editor.")
                break
            elif key == 'n':  # Start creating a new style
                style_name = self.create_new_style()
                if style_name:
                    print(f"Created new style: '{style_name}'")

                # Display the style in edit mode
                self.edit_style(style_name)

            elif key == 's':  # Save styles to file
                self.save_styles()

        if self.menu.alt_buffer:
            pc.write('normal_buffer')



    def display_styles_editor(self):
        """Show the available styles for selection and editing."""
        pc.write('cursor_position', row=self.menu.menu_start_row, col=1)
        for i, style_name in enumerate(self.style_names_to_edit):
            style = self.styles_to_edit[style_name]

            true_color_code = pc.get_color_code('vgreen')
            false_color_code = pc.get_color_code('vred')

            """"
            # Sample preview of the style's attributes
            preview_attr = {
                'color': self.colors.get(style.color, ''),
                'bg_color': self.colors.get(style.bg_color, '').replace('[38', '[48')
            }
            attr_list = [f"{k}={preview_attr[k]}{v}{reset}" for k, v in asdict(style).items()]
            style_line = f"{style_name}: {' | '.join(attr_list)}"
            display_style = self.menu.selected_style if i == self.menu.selected_index else self.menu.unselected_style
            pc.print(style_line, style=display_style)
            """



            color_code = self.colors.get(style.color, '')
            bg_code = color_code.replace('[38', '[48')

            bold_color_code = true_color_code if style.bold else false_color_code
            bold_code = bold_color_code + pc.effect_map.get('bold')

            italic_color_code = true_color_code if style.italic else false_color_code
            italic_code = italic_color_code + pc.effect_map.get('italic')

            ul_color_code = true_color_code if style.underline else false_color_code
            ul_code = ul_color_code + pc.effect_map.get('underline')

            reverse_code_combo = color_code + bg_code + pc.get_effect_code('reverse')
            reverse_code = reverse_code_combo if style.reverse else false_color_code

            dim_color_code = true_color_code if style.dim else false_color_code
            dim_code = dim_color_code + pc.effect_map.get('dim')

            ol_color_code = true_color_code if style.overline else false_color_code
            ol_code = ol_color_code + pc.effect_map.get('overline')

            st_color_code = true_color_code if style.strikethru else false_color_code
            st_code = st_color_code + pc.effect_map.get('strikethru')

            conceal_code = true_color_code if style.conceal else false_color_code

            bl_color_code = true_color_code if style.blink else false_color_code
            bl_code = bl_color_code + pc.effect_map.get('blink')



            attr_list = [
                f"color={color_code}{style.color}{reset}",
                f"bg_color={color_code}{bg_code}{style.bg_color}{reset}",
                f"bold={bold_code}{style.bold}{reset}",
                f"italic={italic_code}{style.italic}{reset}",
                f"underline={ul_code}{style.underline}{reset}",
                f"reverse={reverse_code}{style.reverse}{reset}",
                f"dim={dim_code}{style.dim}{reset}",
                f"overline={ol_code}{style.overline}{reset}",
                f"strikethru={st_code}{style.strikethru}{reset}",
                f"conceal={conceal_code}{style.conceal}{reset}",
                f"blink={bl_code}{style.blink}{reset}"
            ]
            style_line = f"{style_name}: {' | '.join(attr_list)}"
            display_style = self.menu.selected_style if i == self.menu.selected_index else self.menu.unselected_style
            pc.print(style_line, style=display_style)





class StyleMapManager:
    def __init__(self, color_map):
        self.custom_style_map = {
            "default": PStyle(),
        }
        self.color_map = color_map

    def print_available_colors(self):
        """Print available colors."""
        for name, code in self.color_map.items():
            print(f"{code}{name}{reset}", end=" ")
        print()

    def generate_custom_style_map(self):
        """Create or modify style maps interactively."""
        print("Interactive STYLE_MAP creation:")
        while True:
            style_name = input("Enter style name (or 'done'): ").strip()
            if style_name.lower() == 'quit':
                sys.exit(1)
            elif style_name.lower() == 'done':
                break
            attributes = self._get_style_attributes()
            self.custom_style_map[style_name] = PStyle(**attributes)
        return self.custom_style_map

    def _get_style_attributes(self):
        """Prompt user for PStyle attributes."""
        attributes = {}
        color = input("Choose a color (type 'list' to view): ").strip()
        if color.lower() == 'list':
            self.print_available_colors()
            color = input("Choose a color: ").strip()
        attributes['color'] = color if color in self.color_map else None

        bg_color = input("Choose a background color: ").strip()
        attributes['bg_color'] = bg_color if bg_color in self.color_map else None

        for attr in ['bold', 'italic', 'underline', 'strikethru', 'blink']:
            attributes[attr] = input(f"Should this style be {attr}? (True/False): ").strip().lower() == 'true'
        return attributes

    def save_style_map(self, file_path, dict_name):
        """Save the style map to a file."""
        final_style_map_str = "{\n" + ",\n".join(
            [f'    "{name}": PStyle({", ".join(f"{k}={repr(v)}" for k, v in asdict(style).items())})' for name, style in self.custom_style_map.items()]) + "\n}"
        with open(file_path, 'w') as file:
            file.write(f"{dict_name} = {final_style_map_str}\n\n")
        print(f"Saved style map as {dict_name} in {file_path}.")


class ColorMapManager:
    ANSI_256_COLORS = {i: f"\033[38;5;{i}m" for i in range(256)}
    DEFAULT_NAMES = ["black", "red", "green", "yellow", "blue", "magenta", "cyan", "white"]

    def __init__(self, existing_color_map=None):
        """Initialize with an optional existing color map"""
        self.custom_color_map = existing_color_map or {"default": reset}
        if not existing_color_map:
            self.custom_color_map.update({self.DEFAULT_NAMES[i]: self.ANSI_256_COLORS[i] for i in range(8)})

    def print_ansi_256_colors(self, load_existing_color_map):
        """Print the ANSI 256 color table and the custom color map."""
        print(f"\n{self.custom_color_map.get('default', reset)}default{reset}  ***This is the color to print when no color is specified in the print method!\n")
        print('Named Colors:\n')
        if not load_existing_color_map:
            for i in range(8):
                color_code = self.ANSI_256_COLORS[i]
                color_name = [name for name, code in self.custom_color_map.items() if code == color_code and name != 'default']
                color_name = color_name[0] if color_name else self.DEFAULT_NAMES[i]
                print(f"{color_code}{color_name}{reset}", end=" ")
            print("\n\nUnnamed color indexes:\n")
            for i in range(8, 256):
                color_code = self.ANSI_256_COLORS[i]
                color_name = [name for name, code in self.custom_color_map.items() if code == color_code and name != 'default']
                color_name = color_name[0] if color_name else str(i)
                print(f"{color_code}{color_name}{reset}", end=" ")
                if (i + 1) % 16 == 0:
                    print()
        else:
            # Print custom color names first from self.custom_color_map
            for name, color_code in self.custom_color_map.items():
                if name != 'default':  # Skip printing the 'default' entry again
                    print(f"{color_code}{name}{reset}", end=" ")
            print("\n\nRemaining unnamed colors:\n")

            # Now print all remaining colors that are not in self.custom_color_map
            for i in range(256):
                if f"\033[38;5;{i}m" not in self.custom_color_map.values():  # Skip colors already in custom_color_map
                    color_code = self.ANSI_256_COLORS[i]
                    print(f"{color_code}{i}{reset}", end=" ")
                    if (i + 1) % 16 == 0:
                        print()
        print()

    def generate_or_edit_custom_color_map(self, load_existing_color_map=False):
        """Interactively create a new color map."""
        os.system('clear')

        pc.print(f'{pc.apply_indexed_styles(['Prints Charming:', 'Color Map Wizard'], ['pc_title', 'vcyan'])}\n')

        print(' ')

        self.print_ansi_256_colors(load_existing_color_map)

        if not load_existing_color_map:
            ml_string = """
            Existing colors are assigned as follows:
            default (Initially set to the terminal's foreground color)
            0 -> black
            1 -> red
            2 -> green
            3 -> yellow
            4 -> blue
            5 -> magenta
            6 -> cyan
            7 -> white
            """
            print(textwrap.dedent(ml_string))

        while True:
            user_input = input(
                "\nEnter color index and custom name\n (e.g., 12 silver or default <index> or rm <name>), 'done' to finish or 'quit' to exit: ").strip()
            os.system('clear')
            if user_input.lower() == 'quit':
                sys.exit(1)

            elif user_input.lower() in ['done', 'skip', '']:
                break

            elif user_input.lower().startswith('rm '):
                color_name_to_remove = user_input[3:].strip()
                message = self._remove_color(color_name_to_remove)

            elif user_input.lower().startswith('default '):
                message = self._update_default_color(user_input)

            else:
                if ' ' not in user_input:
                    message = "Invalid input. Please enter in the format: <index> <custom_name> or 'rm <name>'."
                    # print("Invalid input. Please enter in the format: <index> <custom_name> or 'rm <name>'.")
                    # continue
                else:
                    message = self._add_color(user_input)

            pc.print(f'{pc.apply_indexed_styles(['Prints Charming:', 'Color Map Wizard'], ['pc_title', 'vcyan'])}\n')

            if message:
                pc.print(f'{message}', style='message')
            else:
                print(' ')

            print(f"\n{self.custom_color_map.get('default', reset)}default{reset}  ***This is the color to print when no color is specified in the print method!\n")

            print('Named Colors:\n')

            # Print named colors first
            for name, code in self.custom_color_map.items():
                if name != 'default':
                    print(f"{code}{name}{reset}", end=" ")
            print("\n" * 2)
            print("Unnamed color indexes:")
            print()
            # Print unnamed colors
            for i in range(256):
                if (ColorMapManager.ANSI_256_COLORS[i] not in self.custom_color_map.values()) or (
                        self.custom_color_map.get('default') == ColorMapManager.ANSI_256_COLORS[i] and 'default' not in self.custom_color_map.values()):
                    print(f"{ColorMapManager.ANSI_256_COLORS[i]}{i}{reset}", end=" ")
                    if (i + 1) % 16 == 0:
                        print()
            print()  # Final newline

        print("\nYour final custom COLOR_MAP dictionary:")
        final_color_map = {"default": self.custom_color_map.get("default", reset)}
        final_color_map.update({name: code for name, code in self.custom_color_map.items() if name != "default"})
        final_color_map_str = "{\n" + ",\n".join([f'    "{name}": "{code.replace(chr(27), "\\033")}"' for name, code in final_color_map.items()]) + "\n}"
        print(final_color_map_str)

        save_to_file = input("\nDo you want to save this color map to a file? (yes/no): ").strip().lower()

        if save_to_file in ['yes', 'y']:

            save_location = input("Do you want to save it within the package? (yes/no): ").strip().lower()
            if save_location in ['yes', 'y']:
                package_path = os.path.join(os.path.dirname(__file__), "color_maps.py")
                file_path = package_path
                mode = 'a'
                existing_dict_names = []
                if os.path.exists(file_path):
                    with open(file_path, 'r') as file:
                        content = file.read()
                        existing_dict_names = re.findall(r'^[A-Za-z_][A-Za-z0-9_]*(?=\s*=\s*\{)', content, re.MULTILINE)
                        print('Previously created color map dictionary names:')
                        print(existing_dict_names)

            else:
                if not sys.platform == 'win32':
                    setup_readline()

                file_path = input("Enter the full file path (tab completion supported): ").strip()

                # Add .py extension if not present
                if not file_path.endswith(".py"):
                    file_path += ".py"

                # Determine whether to append or create a new file
                if os.path.exists(file_path):
                    mode = input("File exists. Do you want to append to it? If no it will ask if you want to overwrite or create a new file (yes/no): ").strip().lower()
                    if mode in ['yes', 'y']:
                        mode = 'a'
                        # Validate dictionary name
                        with open(file_path, 'r') as file:
                            content = file.read()
                            existing_dict_names = re.findall(r'^[A-Za-z_][A-Za-z0-9_]*(?=\s*=\s*\{)', content, re.MULTILINE)
                            print(existing_dict_names)
                    else:
                        mode = 'w'
                        overwrite_or_new = input("Do you want to overwrite the existing file or create a new one? (overwrite/new): ").strip().lower()
                        if overwrite_or_new == 'new':
                            new_file_path = input("Enter the new file name: ").strip()
                            if not new_file_path.endswith(".py"):
                                new_file_path += ".py"
                            file_path = os.path.join(os.path.dirname(file_path), new_file_path)
                        existing_dict_names = []
                else:
                    mode = 'w'
                    existing_dict_names = []

            while True:
                dict_name = input("Give the dictionary a name: ").strip()
                if re.match(r'^[A-Za-z_][A-Za-z0-9_]*$', dict_name):
                    if dict_name not in existing_dict_names:
                        break
                    else:
                        print(f"Dictionary name '{dict_name}' already exists in the file. Please choose a different name.")
                else:
                    print("Invalid dictionary name. Please enter a valid Python variable name.")

            self.save_color_map(file_path, mode, dict_name, final_color_map_str)

        return final_color_map

    def _remove_color(self, color_name):
        if color_name in self.custom_color_map:
            if color_name == 'default':
                self.custom_color_map['default'] = reset
            else:
                del self.custom_color_map[color_name]
            message = f"Removed '{color_name}'"
            return message
            # print(f"Removed '{color_name}'")
        else:
            message = f"'{color_name}' not found."
            return message
            # print(f"'{color_name}' not found.")

    def _update_default_color(self, user_input):
        try:
            index = int(user_input.split()[1])
            if 0 <= index < 256:
                self.custom_color_map['default'] = self.ANSI_256_COLORS[index]
                message = f"Default color changed to index {index}"
                return message
                # print(f"Default color changed to index {index}")
            else:
                message = f"Invalid index: {index}. Index out of range. Please enter a number between 0 and 255."
                return message
                # print(f"Invalid index: {index}. Index out of range. Please enter a number between 0 and 255.")
        except (ValueError, IndexError):
            message = f"Invalid input. Please enter in the format: default <index>."
            return message
            # print("Invalid input. Please enter in the format: default <index>.")

    def _add_color(self, user_input):
        try:
            index_str, custom_name = user_input.split(maxsplit=1)
            index = int(index_str)
            if not re.match(r'^[A-Za-z_][A-Za-z0-9_]*$', custom_name):
                message = f"Invalid color name '{custom_name}'."
                return message
                # print(f"Invalid color name '{custom_name}'.")
                # return
            if 0 <= index < 256:
                self.custom_color_map[custom_name] = self.ANSI_256_COLORS[index]
                return None
            else:
                message = f"Invalid index: {index}. Please enter a number between 0 and 255."
                return message
                # print(f"Invalid index: {index}. Please enter a number between 0 and 255.")
        except ValueError:
            message = "Invalid input. Please enter in the format: <index> <custom_name> or 'rm <name>'."
            return message
            # print("Invalid input. Please enter in the format: <index> <custom_name> or 'rm <name>'.")

    @staticmethod
    def save_color_map(file_path, mode, dict_name, final_color_map_str):
        """Save the color map to a file."""
        # Create the directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, mode) as file:
            file.write(f"{dict_name} = {final_color_map_str}\n\n")
        print(f"color map saved to {file_path} as dictionary name: '{dict_name}'.")


    @staticmethod
    def load_color_maps_from_module(file_path):
        """Load color maps from a Python module file."""
        spec = importlib.util.spec_from_file_location("color_map_module", file_path)
        color_map_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(color_map_module)
        return {name: getattr(color_map_module, name) for name in dir(color_map_module) if isinstance(getattr(color_map_module, name), dict)}


class ColorWizard:
    def __init__(self, args):
        self.args = args
        self.color_manager = None
        self.style_manager = None

    def run(self):
        """Run the wizard for color and style map creation."""
        colors = self._create_or_load_color_map()
        styles = self._create_or_load_style_map()

        return colors, styles

    def _create_or_load_color_map(self):
        """Load or create a color map based on the arguments passed."""

        colors = None

        # Default color map file to 'color_maps.py' if --color-map-name is provided without --color-map-file
        if self.args.color_map_name and not self.args.color_map_file:
            self.args.color_map_file = os.path.join(os.path.dirname(__file__), 'color_maps.py')

        if self.args.color_map_file:
            # Check if the file exists
            if not os.path.exists(self.args.color_map_file):
                print(f"Error: The file '{self.args.color_map_file}' does not exist.")
                sys.exit(1)

            color_maps = ColorMapManager.load_color_maps_from_module(self.args.color_map_file)

            if not color_maps:
                print(f"No color maps found in {self.args.color_map_file}. Exiting.")
                sys.exit(1)

            # If a color map name is specified, load that map
            if self.args.color_map_name:
                if self.args.color_map_name in color_maps:
                    self.color_manager = ColorMapManager(existing_color_map=color_maps[self.args.color_map_name])
                    print(f"Loaded color map '{self.args.color_map_name}'")
                else:
                    print(f"Color map '{self.args.color_map_name}' not found. Available maps: {list(color_maps.keys())}")
                    sys.exit(1)
            else:
                # Let user select the color map if not specified
                print("Available color maps:")
                for color_map_name in color_maps:
                    print(f" - {color_map_name}")

                selected_color_map = input("Enter the name of the color map you want to use: ").strip()

                if selected_color_map in color_maps:
                    self.color_manager = ColorMapManager(existing_color_map=color_maps[selected_color_map])
                    print(f"Selected color map '{selected_color_map}'")
                else:
                    print(f"Color map '{selected_color_map}' not found. Exiting.")
                    sys.exit(1)

            # If the --edit flag is provided, allow editing of the color map
            if self.args.edit:
                print(f"Editing color map '{self.args.color_map_name}'")
                colors = self.color_manager.generate_or_edit_custom_color_map()

        else:
            # Ask the user whether they want to create a new color map or load from color_maps.py
            menu_options = ["color_map_menu", "hor", "Create a new color map.", "Load an existing color map.", "Exit"]
            menu = InteractiveMenu(menu_options, pc=pc, selected_style='vcyan', confirmed_style='vgreen')
            print(f'No color map file or name provided...')

            choice = menu.run()

            if choice in [3, None]:
                sys.exit(1)

            elif choice == 1:
                print("Starting interactive color map creation...")
                self.color_manager = ColorMapManager()
                colors = self.color_manager.generate_or_edit_custom_color_map()


            elif choice == 2:
                color_map_file = os.path.join(os.path.dirname(__file__), 'color_maps.py')

                if not os.path.exists(color_map_file):
                    print(f"Error: The file '{color_map_file}' does not exist.")
                    sys.exit(1)

                color_maps = ColorMapManager.load_color_maps_from_module(color_map_file)

                if not color_maps:
                    print(f"No color maps found in {color_map_file}. Exiting.")
                    sys.exit(1)

                """
                while True:
                    print("Available color maps in 'color_maps.py':")
                    for color_map_name in color_maps:
                        if not color_map_name.startswith("__"):  # Skip __builtins__ and other similar entries
                            print(f" - {color_map_name}")
                    selected_color_map = input("Enter the name of the color map you want to load or 'quit' to exit: ").strip()

                    if selected_color_map == 'quit':
                        sys.exit(1)
                    elif selected_color_map in color_maps:
                        self.color_manager = ColorMapManager(existing_color_map=color_maps[selected_color_map])
                        print(f"Selected color map '{selected_color_map}'")
                        colors = self.color_manager.generate_or_edit_custom_color_map(load_existing_color_map=True)
                        break
                    else:
                        print(f"Color map '{selected_color_map}' not found. Please choose one of the available color maps.")
                        """

                # Prepare the color map selection menu
                color_map_names = [name for name in color_maps if not name.startswith("__")]
                color_map_menu_options = ["color_map_selection", "vert"] + color_map_names + ["Quit"]

                # Create and run the color map selection menu
                color_map_menu = InteractiveMenu(color_map_menu_options, pc=pc, selected_style='vcyan', confirmed_style='vgreen')
                selected_index = color_map_menu.run()

                if selected_index is None or selected_index == len(color_map_names) + 1:  # Quit option
                    sys.exit(1)

                selected_color_map = color_map_names[selected_index - 1]  # Adjust for zero-indexing
                self.color_manager = ColorMapManager(existing_color_map=color_maps[selected_color_map])
                print(f"Selected color map '{selected_color_map}'")
                colors = self.color_manager.generate_or_edit_custom_color_map(load_existing_color_map=True)

            else:
                print("Invalid choice. Exiting.")
                sys.exit(1)

            if colors:
                styles_editor = StylesEditor(menu_instance=menu)
                styles_editor.load_style_editor(colors)
                styles_editor.run_styles_editor()

        return colors

    def _create_or_load_style_map(self):
        """Create or load the style map based on the color map."""
        if not self.color_manager:
            print("Error: No color map loaded or created.")
            sys.exit(1)

        self.style_manager = StyleMapManager(self.color_manager.custom_color_map)
        style_map = self.style_manager.generate_custom_style_map()

        return style_map


def path_completer(text, state):
    """Completes file paths for readline."""
    line = readline.get_line_buffer().split()
    if not line:
        return [text + '/'][state]
    else:
        dir_path = os.path.dirname(line[-1]) or '.'
        base_name = os.path.basename(line[-1])
        matches = [f for f in os.listdir(dir_path) if f.startswith(base_name)]
        matches = [os.path.join(dir_path, match) for match in matches]
        return matches[state] if state < len(matches) else None


def setup_readline():
    readline.set_completer_delims(' \t\n;')
    readline.parse_and_bind("tab: complete")
    readline.set_completer(path_completer)



def main():
    # This is still a work in progress...beyond creating and loading a color_map this is still a work in progress...
    # it's a more organized progression of the original show_colors module which is now the colors_wizard module. Feel free to play around with either though.
    parser = argparse.ArgumentParser(description="Interactive tool for creating custom color and style maps.")
    parser.add_argument("--color-map-file", help="Path to a Python file containing color_map dictionaries", required=False)
    parser.add_argument("--color-map-name", help="Name of the color_map dictionary in the Python file to load", required=False)
    parser.add_argument("--edit", help="Edit the selected color_map before generating the style_map", action="store_true", required=False)

    args = parser.parse_args()

    wizard = ColorWizard(args)
    colors, styles = wizard.run()

    # Example: using the PrintsCharming instance with the generated maps
    custom_pc = PrintsCharming(color_map=wizard.color_manager.custom_color_map, styles=wizard.style_manager.custom_style_map)
    custom_pc.print('This is blue.', color='blue')




def main2():
    menu = InteractiveMenu(
        pc=pc,
        selected_style='vcyan',
        unselected_style='default',
        confirmed_style='vgreen',
    )

    # Create a menu table
    menu_options = ["Edit Styles", "Display Table", "Exit"]
    current_menu_index = [0]  # Track current menu selection index

    # Define a function to get the currently selected menu option text
    def get_menu_option(index):
        return menu_options[index]

    # Menu table data and dynamic highlighting
    menu_table_data = [["Menu Options"]] + [[BoundCell(lambda i=i: menu_options[i])] for i in range(len(menu_options))]

    def menu_style_function(value):
        return 'selected_style' if value == menu_options[current_menu_index[0]] else 'unselected_style'

    table_manager = TableManager(pc)

    # Add menu table to TableManager
    menu_table = table_manager.add_bound_table(
        table_data=menu_table_data,
        table_name="menu_table",
        header_style="cyan",
        border_style="vgreen",
        col_sep_style="vgreen",
        target_text_box=True,
        cell_style=["yellow", "blue"],
        conditional_style_functions={"Menu Options": menu_style_function},
        ephemeral=False,
        append_newline=True,
    )



    # Initialize the menu with its options
    menu.create_menu("main_menu", "vert", menu_options)
    menu.current_menu = "main_menu"  # Set the initial active menu


    # Sensor data generation for table display
    sensor_data = {sensor_id: {
        "temperature": random.uniform(20, 30),
        "humidity": random.uniform(30, 70),
        "pressure": random.uniform(1000, 1020),
        "battery": random.uniform(50, 100),
        "status": "OK"
    } for sensor_id in range(1, 26)}

    # Sensor data update functions
    def get_temperature(sensor_id):
        return round(sensor_data[sensor_id]["temperature"] + random.uniform(-0.5, 0.5), 2)

    def get_humidity(sensor_id):
        return round(sensor_data[sensor_id]["humidity"] + random.uniform(-1, 1), 2)

    def get_pressure(sensor_id):
        return round(sensor_data[sensor_id]["pressure"] + random.uniform(-0.2, 0.2), 2)

    def get_battery(sensor_id):
        return max(round(sensor_data[sensor_id]["battery"] - random.uniform(0.1, 0.5), 2), 0)

    def get_status(sensor_id):
        return "Low Battery" if sensor_data[sensor_id]["battery"] < 20 else "OK"

    def make_bound_cell(func, sensor_id):
        return BoundCell(lambda s_id=sensor_id: func(s_id))

    # Bound table for sensor data
    bound_table_data = [["Sensor ID", "Temperature (°C)", "Humidity (%)", "Pressure (hPa)", "Battery (%)", "Status"]] + [
        [sensor_id, make_bound_cell(get_temperature, sensor_id), make_bound_cell(get_humidity, sensor_id),
         make_bound_cell(get_pressure, sensor_id), make_bound_cell(get_battery, sensor_id),
         make_bound_cell(get_status, sensor_id)]
        for sensor_id in range(1, 26)
    ]

    # Table styling functions
    def battery_style_function(value):
        return 'red' if float(value) < 20 else 'yellow' if float(value) < 50 else 'green'

    def status_style_function(value):
        return 'red' if value == "Low Battery" else 'green'

    # Create TableManager instance and add sensor data table
    table_manager.add_bound_table(
        table_data=bound_table_data,
        table_name="sensor_metrics",
        show_table_name=True,
        header_style="magenta",
        border_style="vgreen",
        col_sep_style="vgreen",
        target_text_box=True,
        cell_style=["orange", "purple"],
        conditional_style_functions={"Battery (%)": battery_style_function, "Status": status_style_function},
        append_newline=True
    )

    # Function to handle menu selection
    def handle_menu_selection():
        selected_option = menu_options[current_menu_index[0]]
        if selected_option == "Edit Styles":
            styles_editor = StylesEditor(menu_instance=menu)
            styles_editor.load_style_editor(colors=pc.color_map, styles=pc.styles)
            styles_editor.run_styles_editor()
        elif selected_option == "Display Table":
            os.system('clear')
            print("\nDisplaying Sensor Metrics:\n")
            table_manager.refresh_bound_table("sensor_metrics")
        elif selected_option == "Exit":
            print("Exiting program.")
            exit()

    os.system('clear')
    # Display both tables and navigate menu
    print(table_manager.tables['menu_table']["generated_table"])

    try:
        while True:
            table_manager.refresh_bound_table("menu_table")
            time.sleep(0.1)



            key = menu.get_key()

            if key in ['k', 'h', pc.ctl_map['arrow_up'], pc.ctl_map['arrow_left']]:
                menu.navigate(-1)
                #current_menu_index[0] = (current_menu_index[0] - 1) % len(menu_options)

            elif key in ['j', 'l', pc.ctl_map['arrow_down'], pc.ctl_map['arrow_right']]:
                menu.navigate(1)
                #current_menu_index[0] = (current_menu_index[0] + 1) % len(menu_options)

            elif key == '\r':
                confirmed_option = menu.menus[menu.current_menu][menu.selected_index]
                handle_menu_selection()
                break

            time.sleep(0.1)  # Adjust the refresh rate as needed
    except KeyboardInterrupt:
        print("\nProgram terminated.")



if __name__ == "__main__":
    pc = PrintsCharming()
    reset = PrintsCharming.RESET

    # Does not work correctly yet
    enable_main2 = False

    if enable_main2:
        #does not work correctly yet
        main2()
    else:
        # works correctly
        main()
