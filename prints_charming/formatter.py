import os






class Formatter:
    def __init__(self, default_width=10, default_precision=2, pad_char=' '):
        """
        Initialize the Formatter with optional default width, precision, and padding character.
        """
        self.default_width = default_width
        self.default_precision = default_precision
        self.pad_char = pad_char


    def get_terminal_width(self):
        terminal_size = os.get_terminal_size()


    def set_default_width(self, width):
        """Update the default width."""
        self.default_width = width


    def set_default_precision(self, precision):
        """Update the default precision."""
        self.default_precision = precision


    def set_pad_char(self, char):
        """Update the default padding character."""
        self.pad_char = char

    # Text alignment and padding
    def left_align(self, text, width=None):
        """Left-align the text using the default width or a custom one."""
        width = width or self.default_width
        return f'{text:<{width}}'


    def right_align(self, text, width=None):
        """Right-align the text using the default width or a custom one."""
        width = width or self.default_width
        return f'{text:>{width}}'


    def center_align(self, text, width=None):
        """Center-align the text using the default width or a custom one."""
        width = width or self.default_width
        return f'{text:^{width}}'


    def pad_with_char_left(self, text, width=None, pad_char=None):
        """Pad the text (left-aligned) using a custom or default padding character and width."""
        width = width or self.default_width
        pad_char = pad_char or self.pad_char
        return f'{text:{pad_char}<{width}}'


    def pad_with_char_right(self, text, width=None, pad_char=None):
        """Pad the text (right-aligned) using a custom or default padding character and width."""
        width = width or self.default_width
        pad_char = pad_char or self.pad_char
        return f'{text:{pad_char}>{width}}'


    def pad_with_char_center(self, text, width=None, pad_char=None):
        """Pad the text (center-aligned) using a custom or default padding character and width."""
        width = width or self.default_width
        pad_char = pad_char or self.pad_char
        return f'{text:{pad_char}^{width}}'


    def truncate_string(self, text, length=None):
        """Truncate the string to a specified length or default width."""
        length = length or self.default_width
        return f'{text:.{length}}'

    # Number formatting
    def format_float(self, number, precision=None):
        """Format a floating-point number with specified decimal places or default precision."""
        if not isinstance(number, (int, float)):
            raise ValueError("Input must be a numeric type")
        precision = precision or self.default_precision
        return f'{number:.{precision}f}'


    def format_percentage(self, ratio, precision=None):
        """Format a number as a percentage with specified or default precision."""
        precision = precision or self.default_precision
        return f'{ratio:.{precision}%}'


    def format_scientific(self, number, precision=None, upper=False):
        """Format a number in scientific notation with default precision."""
        precision = precision or self.default_precision
        return f'{number:.{precision}{("E" if upper else "e")}}'

    def format_with_commas(self, number):
        """Format a number with commas as the thousands separator."""
        return f'{number:,}'

    def format_binary(self, number):
        """Format a number as binary."""
        return f'{number:b}'

    def format_octal(self, number):
        """Format a number as octal."""
        return f'{number:o}'

    def format_hex_lower(self, number):
        """Format a number as hexadecimal (lowercase)."""
        return f'{number:x}'

    def format_hex_upper(self, number):
        """Format a number as hexadecimal (uppercase)."""
        return f'{number:X}'

    def show_sign_for_positive(self, number):
        """Always show the sign for both positive and negative numbers."""
        return f'{number:+}'

    def space_for_positive(self, number):
        """Show a space for positive numbers, minus for negative numbers."""
        return f'{number: }'

    def pad_numbers_with_zeros(self, number, width=None):
        """Pad numbers with leading zeros."""
        width = width or self.default_width
        return f'{number:0{width}}'

    def dynamic_width_and_precision(self, number, width=None, precision=None):
        """Dynamically set width and precision, using defaults if not provided."""
        width = width or self.default_width
        precision = precision or self.default_precision
        return f'{number:{width}.{precision}f}'

    def format_currency(self, amount, precision=None):
        """Format a number as currency with default precision."""
        precision = precision or self.default_precision
        return f'${amount:,.{precision}f}'

    # Object formatting
    def use_str_method(self, obj):
        """Format using str() of the object."""
        return f'{obj!s}'

    def use_repr_method(self, obj):
        """Format using repr() of the object."""
        return f'{obj!r}'

    def use_ascii_method(self, obj):
        """Format using ascii() of the object."""
        return f'{obj!a}'


    def format_dict_as_code(self, dict_name, dictionary, indent=0):
        """
        Format a dictionary to print as it would appear in Python code, including handling nested dictionaries.
        """
        indent_str = "    " * indent  # Adjust indentation based on the depth
        formatted_lines = [f"{indent_str}{dict_name} = {{" if indent == 0 else f"{indent_str}{{"]

        for key, value in dictionary.items():
            if isinstance(value, dict):
                # If the value is a nested dictionary, recursively format it with increased indentation
                formatted_lines.append(f'{indent_str}    "{key}": ' + self.format_dict_as_code("", value, indent + 1))
            else:
                # Otherwise, format the key-value pair normally
                formatted_lines.append(f'{indent_str}    "{key}": "{value}",')

        # Close the dictionary definition
        formatted_lines.append(f"{indent_str}}}")

        # Join all formatted lines into a single string
        return "\n".join(formatted_lines)


    # Optional: Method to format the dictionary and display the keys with ANSI colors from the values
    def format_dict_with_colors(self, dictionary, key_width=None):
        """
        Format a dictionary, applying ANSI color codes to the keys based on the dictionary's values.
        """
        key_width = key_width or max(len(key) for key in dictionary.keys()) + 2  # Adjust width for padding
        formatted_lines = []

        for key, color_code in dictionary.items():
            reset_code = "\033[0m"
            # Apply the color to the key
            formatted_lines.append(f'{color_code}{key:<{key_width}}{reset_code}=> {color_code}{color_code}{reset_code}')

        # Join all formatted lines into a single string
        return "\n".join(formatted_lines)


    def format_multiline_text(self, text, width=None):
        """Format a multi-line string, aligning each line individually."""
        width = width or self.default_width
        lines = text.splitlines()
        return "\n".join(f'{line:<{width}}' for line in lines)


    def format_pos_neg_number(self, number):
        """Conditionally format based on the value (e.g., positive or negative)."""
        return f'{number:+}' if number >= 0 else f'({-number})'



