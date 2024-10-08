# prints_charming/prints_charming_color_wizard.py

import os
import re
import sys
import argparse
import importlib.util
from dataclasses import asdict

if not sys.platform == 'win32':
    import readline
from .prints_charming import PrintsCharming
from .prints_style import PStyle
from .table_manager import TableManager


RESET = PrintsCharming.RESET


ANSI_256_COLORS = {i: f"\033[38;5;{i}m" for i in range(256)}
DEFAULT_NAMES = ["black", "red", "green", "yellow", "blue", "magenta", "cyan", "white"]









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


def load_color_maps_from_module(file_path):
    """Loads all color_map dictionaries from a module."""
    spec = importlib.util.spec_from_file_location("color_map_module", file_path)
    color_map_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(color_map_module)

    # Find all dictionaries defined in the module that are named 'color_map_*'
    color_maps = {name: getattr(color_map_module, name)
                  for name in dir(color_map_module) if isinstance(getattr(color_map_module, name), dict)}

    return color_maps


def print_ansi_256_colors(custom_color_map):
    print()
    print("Current COLOR_MAP dictionary keys:")
    print()
    # Print the default color
    print(f"{custom_color_map.get('default', RESET)}default{RESET}  ***The instance will default to printing in this color if a color is not specified in the print method!")
    print()

    # Print first 8 colors with custom names if available
    for i in range(8):
        color_code = ANSI_256_COLORS[i]
        color_name = [name for name, code in custom_color_map.items() if code == color_code and name != 'default']
        color_name = color_name[0] if color_name else DEFAULT_NAMES[i]
        print(f"{color_code}{color_name}{RESET}", end=" ")
    print("\n" * 2)
    print("Unnamed color indexes:")
    print()

    # Print all other colors with custom names if available
    for i in range(8, 256):
        color_code = ANSI_256_COLORS[i]
        color_name = [name for name, code in custom_color_map.items() if code == color_code and name != 'default']
        color_name = color_name[0] if color_name else str(i)
        print(f"{color_code}{color_name}{RESET}", end=" ")
        if (i + 1) % 16 == 0:
            print()  # Newline after every 16 colors
    print()  # Final newline


def generate_custom_color_map(existing_color_map=None):
    # custom_color_map = {"default": RESET}
    """Create or modify a color map interactively."""
    custom_color_map = existing_color_map or {"default": RESET}
    custom_color_map.update({DEFAULT_NAMES[i]: ANSI_256_COLORS[i] for i in range(8)})
    os.system('clear')
    print("Interactive COLOR_MAP creation:")
    print_ansi_256_colors(custom_color_map)

    print("Existing colors are assigned as follows:")
    print("default (Initially set to the terminal's foreground color)")
    print("0 -> black")
    print("1 -> red")
    print("2 -> green")
    print("3 -> yellow")
    print("4 -> blue")
    print("5 -> magenta")
    print("6 -> cyan")
    print("7 -> white")

    while True:
        user_input = input("\nEnter color index and custom name\n (e.g., 12 silver or 160 red or default <index> to change default), 'rm <name>' to remove, or 'done' to finish: ").strip()
        os.system('clear')  # Clear the screen after each input
        if user_input.lower() == 'done':
            break

        if user_input.lower().startswith('rm '):
            color_name_to_remove = user_input[3:].strip()
            if color_name_to_remove in custom_color_map:
                if color_name_to_remove == 'default':
                    custom_color_map['default'] = RESET
                else:
                    del custom_color_map[color_name_to_remove]
                print(f"Removed color '{color_name_to_remove}'")
            else:
                print(f"Color name '{color_name_to_remove}' not found.")
        elif user_input.lower().startswith('default '):
            try:
                index = int(user_input.split()[1])
                if 0 <= index < 256:
                    custom_color_map['default'] = ANSI_256_COLORS[index]
                    print(f"Default color changed to index {index}")
                else:
                    print(f"Invalid index: {index}. Please enter a number between 0 and 255.")
            except (ValueError, IndexError):
                print("Invalid input. Please enter in the format: default <index>.")
        else:
            if ' ' not in user_input:
                print("Invalid input. Please enter in the format: <index> <custom_name> or 'rm <name>'.")
                continue

            try:
                index_str, custom_name = user_input.split(maxsplit=1)
                index = int(index_str)
                if not re.match(r'^[A-Za-z_][A-Za-z0-9_]*$', custom_name):
                    print(f"Invalid color name '{custom_name}'. Please enter a valid Python variable name.")
                    continue
                if 0 <= index < 256:
                    custom_color_map[custom_name] = ANSI_256_COLORS[index]
                else:
                    print(f"Invalid index: {index}. Please enter a number between 0 and 255.")
            except ValueError:
                print("Invalid input. Please enter in the format: <index> <custom_name> or 'rm <name>'.")

        print("\nCurrent COLOR_MAP dictionary keys:")
        print()
        # Print the default color
        print(f"{custom_color_map.get('default', RESET)}default{RESET}  ***The instance will default to printing in this color if a color is not specified!")
        print()
        # Print named colors first
        for name, code in custom_color_map.items():
            if name != 'default':
                print(f"{code}{name}{RESET}", end=" ")
        print("\n" * 2)
        print("Unnamed color indexes:")
        print()
        # Print unnamed colors
        for i in range(256):
            if (ANSI_256_COLORS[i] not in custom_color_map.values()) or (custom_color_map.get('default') == ANSI_256_COLORS[i] and 'default' not in custom_color_map.values()):
                print(f"{ANSI_256_COLORS[i]}{i}{RESET}", end=" ")
                if (i + 1) % 16 == 0:
                    print()
        print()  # Final newline

    print("\nYour final custom COLOR_MAP dictionary:")
    final_color_map = {"default": custom_color_map.get("default", RESET)}
    final_color_map.update({name: code for name, code in custom_color_map.items() if name != "default"})
    final_color_map_str = "{\n" + ",\n".join([f'    "{name}": "{code.replace(chr(27), "\\033")}"' for name, code in final_color_map.items()]) + "\n}"
    print(final_color_map_str)

    save_to_file = input("\nDo you want to save this COLOR_MAP to a file? (yes/no): ").strip().lower()
    #if save_to_file in ['yes', 'y'] and not sys.platform == 'win32':
        #setup_readline()

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

        # Create the directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)


        with open(file_path, mode) as file:
            file.write(f"{dict_name} = {final_color_map_str}\n\n")
        print(f"COLOR_MAP saved to {file_path} as dictionary name: '{dict_name}'.")

        return file_path, dict_name, final_color_map



def save_style_map_to_file(custom_style_map):
    final_style_map_str = "{\n" + ",\n".join(
        [f'    "{name}": PStyle({", ".join(f"{k}={repr(v)}" for k, v in asdict(style).items())})'
         for name, style in custom_style_map.items()]) + "\n}"

    file_path = input("Enter the file path to save (e.g., custom_styles.py): ").strip()

    # Add .py extension if not present
    if not file_path.endswith(".py"):
        file_path += ".py"

    dict_name = input("Give the dictionary a name: ").strip()

    # Create the directory if it doesn't exist
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with open(file_path, 'w') as file:
        file.write(f"{dict_name} = {final_style_map_str}\n\n")

    print(f"STYLE_MAP saved to {file_path} as dictionary name: '{dict_name}'.")

    return file_path, dict_name, custom_style_map


def generate_custom_style_map(color_map):
    custom_style_map = {
        "default": PStyle(),
    }

    def print_available_colors():
        print("\nAvailable Colors (from color_map):\n")
        for name, code in color_map.items():
            print(f"{code}{name}{RESET}", end=" ")
        print("\n")

    def print_current_styles():
        print("\nCurrent STYLE_MAP dictionary:\n")
        for name, style in custom_style_map.items():
            style_str = f"{name}: {style}"
            styled_name = f"{color_map.get(style.color, '')}{style.color or ''}{RESET}"
            print(f"{styled_name}{name}{RESET}")
            print(f"Attributes: {style_str}")
        print("\n")

    def get_pstyle_attributes():
        """Prompt the user for PStyle attributes interactively."""
        attributes = {}

        color = input("Choose a color (type 'list' to see all colors): ").strip()
        if color.lower() == 'list':
            print_available_colors()
            color = input("Choose a color: ").strip()

        if color in color_map:
            attributes['color'] = color
        else:
            print(f"Invalid color. Using default.")

        bg_color = input("Choose a background color (type 'list' to see all bg colors, or leave blank for none): ").strip()
        if bg_color.lower() == 'list':
            print_available_colors()
            bg_color = input("Choose a background color: ").strip()

        if bg_color in color_map:
            attributes['bg_color'] = bg_color
        else:
            attributes['bg_color'] = None

        for attr in ['bold', 'italic', 'underline', 'overline', 'strikethru', 'conceal', 'blink', 'reverse']:
            value = input(f"Should this style be {attr}? (True/False): ").strip().lower()
            attributes[attr] = True if value == 'true' else False

        return attributes

    os.system('clear')
    print("Interactive STYLE_MAP creation:")
    print("You can create custom styles by specifying various attributes like color, bg_color, bold, italic, etc.")
    print("To exit, type 'done'. To remove a style, type 'rm <name>'.\n")

    print_available_colors()

    while True:
        print_current_styles()
        user_input = input("\nEnter style name or 'done' to finish: ").strip()
        if user_input.lower() == 'done':
            break
        elif user_input.lower().startswith('rm '):
            style_name = user_input[3:].strip()
            if style_name in custom_style_map:
                del custom_style_map[style_name]
                print(f"Removed style '{style_name}'")
            else:
                print(f"Style name '{style_name}' not found.")
        else:
            style_name = user_input
            if not re.match(r'^[A-Za-z_][A-Za-z0-9_]*$', style_name):
                print(f"Invalid style name '{style_name}'. Please enter a valid Python variable name.")
                continue

            print(f"\nCreating/Updating style '{style_name}'")
            attributes = get_pstyle_attributes()

            custom_style_map[style_name] = PStyle(**attributes)

    save_to_file = input("\nDo you want to save this STYLE_MAP to a file? (yes/no): ").strip().lower()
    if save_to_file in ['yes', 'y']:
        file_path, dict_name, final_style_map = save_style_map_to_file(custom_style_map)
        return file_path, dict_name, final_style_map

    return None, None, custom_style_map




def main():
    # This is still a work in progress...beyond creating and loading a color_map and creating a styles_map this is still a work in progress...
    # Future development will be in the interactive_wizard module. Feel free to play around with either though.
    parser = argparse.ArgumentParser(description="Interactive tool for creating custom style maps.")
    parser.add_argument("--color-map-file", help="Path to a Python file containing one or more 'color_map' dictionaries", required=False)
    parser.add_argument("--color-map-name", help="Name of the color_map dictionary in the Python file to load", required=False)
    parser.add_argument("--edit", help="Edit the selected color_map before generating the style_map", action="store_true", required=False)

    args = parser.parse_args()

    # Default color map file to 'color_maps.py' if --color-map-name is provided without --color-map-file
    if args.color_map_name and not args.color_map_file:
        args.color_map_file = os.path.join(os.path.dirname(__file__), 'color_maps.py')

    # Initialize the final_color_map to None
    final_color_map = None

    # Check if the user provided a color_map file
    if args.color_map_file:
        # Check if the file exists
        if not os.path.exists(args.color_map_file):
            print(f"Error: The file '{args.color_map_file}' does not exist.")
            sys.exit(1)

        try:
            # Load all color_maps from the given file
            color_maps = load_color_maps_from_module(args.color_map_file)

            if not color_maps:
                print(f"No color maps found in {args.color_map_file}. Exiting.")
                sys.exit(1)

            # If the user provided a specific color_map_name, use that
            if args.color_map_name:
                if args.color_map_name in color_maps:
                    final_color_map = color_maps[args.color_map_name]
                    print(f"Loaded color_map '{args.color_map_name}' from {args.color_map_file}")
                else:
                    print(f"Color map '{args.color_map_name}' not found in {args.color_map_file}. Available maps: {list(color_maps.keys())}")
                    sys.exit(1)
            else:
                # List available color maps if the user hasn't provided a specific one
                print("Available color maps:")
                for color_map_name in color_maps:
                    print(f" - {color_map_name}")

                selected_color_map = input("Enter the name of the color map you want to use: ").strip()

                if selected_color_map in color_maps:
                    final_color_map = color_maps[selected_color_map]
                    print(f"Selected color map '{selected_color_map}'")
                else:
                    print(f"Color map '{selected_color_map}' not found. Exiting.")
                    sys.exit(1)

            # If the --edit flag is provided, allow editing of the color_map
            if args.edit:
                print(f"Editing color map '{args.color_map_name}'")
                final_color_map = generate_custom_color_map(existing_color_map=final_color_map)

        except Exception as e:
            print(f"Error loading color map from file: {e}")
            sys.exit(1)

    # If no color_map_file or color_map_name is provided, generate a new color map
    if final_color_map is None:
        print("No color map file or color map name provided. Starting interactive color map creation...")
        file_path_color_map, dict_name_color_map, final_color_map = generate_custom_color_map()

    # Now create the style map using the loaded or generated color map
    file_path_style_map, dict_name_style_map, final_style_map = generate_custom_style_map(final_color_map)

    # Example: using the PrintsCharming instance with the generated maps
    custom_pc = PrintsCharming(color_map=final_color_map, styles=final_style_map) if file_path_style_map and dict_name_style_map and final_style_map else None
    custom_pc.print('This is blue.', color='blue') if custom_pc.color_map.get('blue') else None
    custom_pc.print('This is a custom bold style.', style='blue') if custom_pc.styles.get('blue') else None



if __name__ == "__main__":
    main()








