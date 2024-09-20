# prints_charming/interactive_wizard.py

import os
import re
import sys
import argparse
import textwrap
import importlib.util
from dataclasses import asdict

if not sys.platform == 'win32':
    import readline
from .prints_charming import PrintsCharming
from .prints_style import PStyle
from .interactive_menu import InteractiveMenu

from .prints_charming_defaults import (
    DEFAULT_COLOR_MAP,
    DEFAULT_STYLES
)


RESET = PrintsCharming.RESET


class ColorMapManager:
    ANSI_256_COLORS = {i: f"\033[38;5;{i}m" for i in range(256)}
    DEFAULT_NAMES = ["black", "red", "green", "yellow", "blue", "magenta", "cyan", "white"]

    def __init__(self, existing_color_map=None):
        """Initialize with an optional existing color map"""
        self.custom_color_map = existing_color_map or {"default": RESET}
        if not existing_color_map:
            self.custom_color_map.update({self.DEFAULT_NAMES[i]: self.ANSI_256_COLORS[i] for i in range(8)})

    def print_ansi_256_colors(self, load_existing_color_map):
        """Print the ANSI 256 color table and the custom color map."""
        print(f"\n{self.custom_color_map.get('default', RESET)}default{RESET}  ***This is the color to print when no color is specified in the print method!\n")
        print('Named Colors:\n')
        if not load_existing_color_map:
            for i in range(8):
                color_code = self.ANSI_256_COLORS[i]
                color_name = [name for name, code in self.custom_color_map.items() if code == color_code and name != 'default']
                color_name = color_name[0] if color_name else self.DEFAULT_NAMES[i]
                print(f"{color_code}{color_name}{RESET}", end=" ")
            print("\n\nUnnamed color indexes:\n")
            for i in range(8, 256):
                color_code = self.ANSI_256_COLORS[i]
                color_name = [name for name, code in self.custom_color_map.items() if code == color_code and name != 'default']
                color_name = color_name[0] if color_name else str(i)
                print(f"{color_code}{color_name}{RESET}", end=" ")
                if (i + 1) % 16 == 0:
                    print()
        else:
            # Print custom color names first from self.custom_color_map
            for name, color_code in self.custom_color_map.items():
                if name != 'default':  # Skip printing the 'default' entry again
                    print(f"{color_code}{name}{RESET}", end=" ")
            print("\n\nRemaining unnamed colors:\n")

            # Now print all remaining colors that are not in self.custom_color_map
            for i in range(256):
                if f"\033[38;5;{i}m" not in self.custom_color_map.values():  # Skip colors already in custom_color_map
                    color_code = self.ANSI_256_COLORS[i]
                    print(f"{color_code}{i}{RESET}", end=" ")
                    if (i + 1) % 16 == 0:
                        print()
        print()



    def generate_or_edit_custom_color_map(self, load_existing_color_map=False):
        """Interactively create a new color map."""
        os.system('clear')


        pc.print(f'{pc.apply_index_style(['Prints Charming:', 'Color Map Wizard'], ['pc_title', 'vcyan'])}\n')

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

            elif user_input.lower() == 'done':
                break

            elif user_input.lower().startswith('rm '):
                color_name_to_remove = user_input[3:].strip()
                message = self._remove_color(color_name_to_remove)

            elif user_input.lower().startswith('default '):
                message = self._update_default_color(user_input)

            else:
                if ' ' not in user_input:
                    message = "Invalid input. Please enter in the format: <index> <custom_name> or 'rm <name>'."
                    #print("Invalid input. Please enter in the format: <index> <custom_name> or 'rm <name>'.")
                    #continue
                else:
                    message = self._add_color(user_input)


            pc.print(f'{pc.apply_index_style(['Prints Charming:', 'Color Map Wizard'], ['pc_title', 'vcyan'])}\n')

            if message:
                pc.print(f'{message}', style='message')
            else:
                print(' ')

            print(f"\n{self.custom_color_map.get('default', RESET)}default{RESET}  ***This is the color to print when no color is specified in the print method!\n")

            print('Named Colors:\n')

            # Print named colors first
            for name, code in self.custom_color_map.items():
                if name != 'default':
                    print(f"{code}{name}{RESET}", end=" ")
            print("\n" * 2)
            print("Unnamed color indexes:")
            print()
            # Print unnamed colors
            for i in range(256):
                if (ColorMapManager.ANSI_256_COLORS[i] not in self.custom_color_map.values()) or (
                        self.custom_color_map.get('default') == ColorMapManager.ANSI_256_COLORS[i] and 'default' not in self.custom_color_map.values()):
                    print(f"{ColorMapManager.ANSI_256_COLORS[i]}{i}{RESET}", end=" ")
                    if (i + 1) % 16 == 0:
                        print()
            print()  # Final newline

        print("\nYour final custom COLOR_MAP dictionary:")
        final_color_map = {"default": self.custom_color_map.get("default", RESET)}
        final_color_map.update({name: code for name, code in self.custom_color_map.items() if name != "default"})
        final_color_map_str = "{\n" + ",\n".join([f'    "{name}": "{code.replace(chr(27), "\\033")}"' for name, code in final_color_map.items()]) + "\n}"
        print(final_color_map_str)

        save_to_file = input("\nDo you want to save this color map to a file? (yes/no): ").strip().lower()

        if save_to_file in ['yes', 'y']:
            if not sys.platform == 'win32':
                setup_readline()

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

                file_path = input("Enter the full file path: ").strip()

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
                self.custom_color_map['default'] = RESET
            else:
                del self.custom_color_map[color_name]
            message = f"Removed '{color_name}'"
            return message
            #print(f"Removed '{color_name}'")
        else:
            message = f"'{color_name}' not found."
            return message
            #print(f"'{color_name}' not found.")

    def _update_default_color(self, user_input):
        try:
            index = int(user_input.split()[1])
            if 0 <= index < 256:
                self.custom_color_map['default'] = self.ANSI_256_COLORS[index]
                message = f"Default color changed to index {index}"
                return message
                #print(f"Default color changed to index {index}")
            else:
                message = f"Invalid index: {index}. Index out of range. Please enter a number between 0 and 255."
                return message
                #print(f"Invalid index: {index}. Index out of range. Please enter a number between 0 and 255.")
        except (ValueError, IndexError):
            message = f"Invalid input. Please enter in the format: default <index>."
            return message
            #print("Invalid input. Please enter in the format: default <index>.")

    def _add_color(self, user_input):
        try:
            index_str, custom_name = user_input.split(maxsplit=1)
            index = int(index_str)
            if not re.match(r'^[A-Za-z_][A-Za-z0-9_]*$', custom_name):
                message = f"Invalid color name '{custom_name}'."
                return message
                #print(f"Invalid color name '{custom_name}'.")
                #return
            if 0 <= index < 256:
                self.custom_color_map[custom_name] = self.ANSI_256_COLORS[index]
                return None
            else:
                message = f"Invalid index: {index}. Please enter a number between 0 and 255."
                return message
                #print(f"Invalid index: {index}. Please enter a number between 0 and 255.")
        except ValueError:
            message = "Invalid input. Please enter in the format: <index> <custom_name> or 'rm <name>'."
            return message
            #print("Invalid input. Please enter in the format: <index> <custom_name> or 'rm <name>'.")


    def save_color_map(self, file_path, mode, dict_name, final_color_map_str):
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




class StyleMapManager:
    def __init__(self, color_map):
        self.custom_style_map = {
            "default": PStyle(),
        }
        self.color_map = color_map

    def print_available_colors(self):
        """Print available colors."""
        for name, code in self.color_map.items():
            print(f"{code}{name}{RESET}", end=" ")
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
        final_style_map_str = "{\n" + ",\n".join([f'    "{name}": PStyle({", ".join(f"{k}={repr(v)}" for k, v in asdict(style).items())})' for name, style in self.custom_style_map.items()]) + "\n}"
        with open(file_path, 'w') as file:
            file.write(f"{dict_name} = {final_style_map_str}\n\n")
        print(f"Saved style map as {dict_name} in {file_path}.")


class ColorWizard:
    def __init__(self, args):
        self.args = args
        self.color_manager = None
        self.style_manager = None

    def run(self):
        """Run the wizard for color and style map creation."""
        self._create_or_load_color_map()
        self._create_or_load_style_map()

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
            menu = InteractiveMenu('vcyan', menu_options, pc=pc, confirmed_style='vgreen')
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

            else:
                print("Invalid choice. Exiting.")
                sys.exit(1)

            if colors:
                menu.load_style_editor(colors)
                menu.run_styles_editor()

        return colors


    def _create_or_load_style_map(self):
        """Create or load the style map based on the color map."""
        if not self.color_manager:
            print("Error: No color map loaded or created.")
            sys.exit(1)

        self.style_manager = StyleMapManager(self.color_manager.custom_color_map)
        self.style_manager.generate_custom_style_map()


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
    wizard.run()


    # Example: using the PrintsCharming instance with the generated maps
    custom_pc = PrintsCharming(color_map=wizard.color_manager.custom_color_map, styles=wizard.style_manager.custom_style_map)
    custom_pc.print('This is blue.', color='blue')



if __name__ == "__main__":
    pc = PrintsCharming(color_map=DEFAULT_COLOR_MAP.copy(), styles=DEFAULT_STYLES.copy())
    main()
