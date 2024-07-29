# prints_charming/show_colors.py

import os
import re
import sys

if not sys.platform == 'win32':
    import readline
from .prints_charming import PrintsCharming, TextStyle, TableManager


RESET = PrintsCharming.RESET


ANSI_256_COLORS = {i: f"\033[38;5;{i}m" for i in range(256)}
DEFAULT_NAMES = ["black", "red", "green", "yellow", "blue", "magenta", "cyan", "white"]


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


def generate_custom_color_map():
    custom_color_map = {"default": RESET}
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
    if save_to_file in ['yes', 'y'] and not sys.platform == 'win32':
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



if __name__ == "__main__":
    generate_custom_color_map()








