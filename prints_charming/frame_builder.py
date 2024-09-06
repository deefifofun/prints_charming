import re
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from .prints_charming_defaults import (
    DEFAULT_CONFIG,
    DEFAULT_COLOR_MAP,
    DEFAULT_EFFECT_MAP,
    DEFAULT_STYLES,
    DEFAULT_LOGGING_STYLES
)

from .prints_charming import PrintsCharming
from .utils import get_terminal_width





class FrameBuilder:
    def __init__(self, pc=None, horiz_width=None, horiz_char=' ', vert_width=None, vert_padding=1, vert_char='|'):
        self.pc = pc if pc else PrintsCharming()
        self.terminal_width = get_terminal_width()
        self.horiz_width = horiz_width if horiz_width else self.terminal_width
        self.horiz_char = horiz_char
        self.horiz_border = self.horiz_width * horiz_char
        self.vert_width = vert_width
        self.vert_padding = vert_padding * ' '
        self.vert_char = horiz_char if vert_width and not vert_char else vert_char
        self.vert_border = '' if not vert_width else vert_width * self.vert_char
        self.available_width = None


    def align_text(self, text, available_width, align='center'):

        if align == 'left':
            return text.ljust(available_width)
        elif align == 'right':
            return text.rjust(available_width)
        elif align == 'center':
            return text.center(available_width)
        else:
            raise ValueError("Invalid alignment. Choose from 'left', 'right', or 'center'.")



    def align_strings(self, strings, available_width=None, styles=None, alignments=None):
        if len(strings) not in [2, 3]:
            raise ValueError("The list must contain exactly two or three strings.")

        if not available_width:
            available_width = self.get_available_width()

        if len(strings) == 3:
            part_width = available_width // 3
            remainder = available_width % 3

            if remainder != 0:
                left_right_width = (available_width - (part_width + remainder)) // 2
                center_width = part_width + remainder
            else:
                left_right_width = part_width
                center_width = part_width

            # Check if any string is too long
            for i, string in enumerate(strings):
                if i == 1:  # Center part
                    max_width = center_width
                else:  # Left and right parts
                    max_width = left_right_width

                if len(string) > max_width:
                    raise ValueError(f"String at index {i} ('{string}') is too long. "
                                     f"Section width: {max_width}, String length: {len(string)}")

            if not styles:
                styles = ['default', 'default', 'default']
            if isinstance(styles, str):
                styles = [styles, styles, styles]

            if not alignments:
                alignments = ['center', 'center', 'center']
            if isinstance(alignments, str):
                alignments = [alignments, alignments, alignments]

            left_aligned = self.pc.apply_style(styles[0], self.align_text(strings[0], left_right_width, alignments[0]))
            center_aligned = self.pc.apply_style(styles[1], self.align_text(strings[1], center_width, alignments[1]))
            right_aligned = self.pc.apply_style(styles[2], self.align_text(strings[2], left_right_width, alignments[2]))

            # Concatenate the aligned strings
            return left_aligned + center_aligned + right_aligned


        elif len(strings) == 2:
            # Determine the width for each section
            part_width = available_width // 2

            # Check if any string is too long
            for i, string in enumerate(strings):
                if len(string) > part_width:
                    raise ValueError(f"String at index {i} ('{string}') is too long. "
                                     f"Section width: {part_width}, String length: {len(string)}")

            if not styles:
                styles = ['default', 'default']
            if isinstance(styles, str):
                styles = [styles, styles]

            if not alignments:
                alignments = ['center', 'center']
            if isinstance(alignments, str):
                alignments = [alignments, alignments]

            left_aligned = self.pc.apply_style(styles[0], self.align_text(strings[0], part_width, alignments[0]))
            right_aligned = self.pc.apply_style(styles[1], self.align_text(strings[1], part_width, alignments[1]))

            # Concatenate the aligned strings
            return left_aligned + right_aligned


    def split_text_to_lines_v2(self, text, available_width):
        lines = text.split('\n')
        split_lines = []
        for line in lines:
            words = line.split()
            current_line = ""
            for word in words:
                if len(current_line) + len(word) + 1 <= available_width:
                    if current_line:
                        current_line += " "
                    current_line += word
                else:
                    split_lines.append(current_line)
                    current_line = word
            if current_line:
                split_lines.append(current_line)
        return split_lines


    def split_text_to_lines(self, text, available_width):
        words = text.split()
        lines = []
        current_line = ""
        for word in words:
            if len(current_line) + len(word) + 1 <= available_width:
                if current_line:
                    current_line += " "
                current_line += word
            else:
                lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
        return lines


    def get_available_width(self):
        if self.available_width is None:
            self.available_width = (
                self.horiz_width - (2 * self.vert_width) - (len(self.vert_padding) * 2)
                if self.vert_border
                else self.horiz_width - (len(self.vert_padding) * 2)
            )
        return self.available_width


    def strip_ansi_escape_sequences(self, text):
        ansi_escape = re.compile(r'\x1b\[([0-9]+)(;[0-9]+)*m')
        return ansi_escape.sub('', text)

    def print_simple_border_boxed_text(self, title, subtitle='', align='center'):
        available_width = self.get_available_width()

        title_aligned_text = self.pc.apply_style('vgreen', self.align_text(title, available_width, align))

        if subtitle:
            subtitle_aligned_text = self.pc.apply_style('white', self.align_text(subtitle, available_width, align))
        else:
            subtitle_aligned_text = ''

        horiz_border_top = self.pc.apply_style('purple', self.horiz_border)
        horiz_border_bottom = self.pc.apply_style('orange', self.horiz_border)

        title_vert_border_left = self.pc.apply_style('orange', self.vert_border) + self.vert_padding
        title_vert_border_right = self.vert_padding + self.pc.apply_style('purple', self.vert_border)

        subtitle_vert_border_left = self.pc.apply_style('orange', self.vert_border) + self.vert_padding
        subtitle_vert_border_right = self.vert_padding + self.pc.apply_style('purple', self.vert_border)

        formatted_title_line = f"{title_vert_border_left}{title_aligned_text}{title_vert_border_right}"
        if subtitle:
            formatted_subtitle_line = f"{subtitle_vert_border_left}{subtitle_aligned_text}{subtitle_vert_border_right}"

        print(horiz_border_top)
        print(formatted_title_line)
        if subtitle:
            print(formatted_subtitle_line)
        print(horiz_border_bottom)
        print()


    def build_styled_border_box(self, horiz_border_top=True, horiz_border_top_style=None,
                                horiz_border_bottom=True, horiz_border_bottom_style=None,
                                vert_border_left=True, vert_border_left_style=None,
                                vert_border_right=True, vert_border_right_style=None):

        if horiz_border_top:
            horiz_border_top = self.horiz_border if not horiz_border_top_style else self.pc.apply_style(horiz_border_top_style, self.horiz_border)
        else:
            horiz_border_top = None

        if horiz_border_bottom:
            horiz_border_bottom = self.horiz_border if not horiz_border_bottom_style else self.pc.apply_style(horiz_border_bottom_style, self.horiz_border)
        else:
            horiz_border_bottom = None

        if self.vert_char == ' ':
            if vert_border_left:
                vert_border_left = self.vert_border + self.vert_padding if not vert_border_left_style else self.pc.apply_bg_color(vert_border_left_style, self.vert_border) + self.vert_padding
            else:
                vert_border_left = self.vert_padding

            if vert_border_right:
                vert_border_right = self.vert_padding + self.vert_border if not vert_border_right_style else self.vert_padding + self.pc.apply_bg_color(vert_border_right_style, self.vert_border)
            else:
                vert_border_right = self.vert_padding

        else:
            if vert_border_left:
                vert_border_left = self.vert_border + self.vert_padding if not vert_border_left_style else self.pc.apply_style(vert_border_left_style, self.vert_border) + self.vert_padding
            else:
                vert_border_left = self.vert_padding

            if vert_border_right:
                vert_border_right = self.vert_padding + self.vert_border if not vert_border_right_style else self.vert_padding + self.pc.apply_style(vert_border_right_style, self.vert_border)
            else:
                vert_border_right = self.vert_padding



        return horiz_border_top, vert_border_left, vert_border_right, horiz_border_bottom


    def construct_text(self, vert_border_left, vert_border_right, aligned_text):
        # Define a dictionary mapping conditions to their corresponding text constructions
        construction_map = {
            (True, True): lambda: f"{vert_border_left}{aligned_text}{vert_border_right}",
            (True, False): lambda: f"{vert_border_left}{aligned_text}",
            (False, True): lambda: f"{aligned_text}{vert_border_right}",
            (False, False): lambda: aligned_text
        }

        # Determine the key based on the presence of the borders
        key = (bool(vert_border_left), bool(vert_border_right))

        # Construct and return the text based on the mapped lambda function
        return construction_map[key]()



    def print_border_boxed_text(self, text, text_style=None, text_align='center',
                                subtext='', subtext_style=None, subtext_align='center',
                                horiz_border_top=True, horiz_border_top_style=None,
                                horiz_border_bottom=True, horiz_border_bottom_style=None,
                                text_vert_border_l_style=None, text_vert_border_r_style=None,
                                subtext_vert_border_l_style=None, subtext_vert_border_r_style=None,
                                first_line_blank=False):

        if not text_style:
            text_style = 'default'
        if not subtext_style:
            subtext_style = 'default'

        available_width = self.get_available_width()
        text_lines = self.split_text_to_lines(text, available_width)
        subtext_lines = self.split_text_to_lines(subtext, available_width) if subtext else []

        if horiz_border_top:
            horiz_border_top = self.horiz_border if not horiz_border_top_style else self.pc.apply_style(horiz_border_top_style, self.horiz_border)
            print(horiz_border_top)

        if first_line_blank:
            blank_text = ' '
            blank_aligned_text = self.align_text(blank_text, available_width, text_align)
            if self.vert_border:
                blank_text_vert_border_left = self.vert_border + self.vert_padding if not text_vert_border_l_style else self.pc.apply_style(text_vert_border_l_style, self.vert_border) + self.vert_padding
                blank_text_vert_border_right = self.vert_padding + self.vert_border + self.vert_padding if not text_vert_border_r_style else self.vert_padding + self.pc.apply_style(text_vert_border_r_style, self.vert_border)
                print(f"{blank_text_vert_border_left}{blank_aligned_text}{blank_text_vert_border_right}")
            else:
                print(f"{self.vert_padding}{blank_aligned_text}{self.vert_padding}")


        for line in text_lines:
            aligned_text = self.pc.apply_style(text_style, self.align_text(line, available_width, text_align))
            if self.vert_border:
                text_vert_border_left = self.vert_border + self.vert_padding if not text_vert_border_l_style else self.pc.apply_style(text_vert_border_l_style, self.vert_border) + self.vert_padding
                text_vert_border_right = self.vert_padding + self.vert_border + self.vert_padding if not text_vert_border_r_style else self.vert_padding + self.pc.apply_style(text_vert_border_r_style, self.vert_border)
                print(f"{text_vert_border_left}{aligned_text}{text_vert_border_right}")
            else:
                txt_vert_border_left = self.vert_padding
                txt_vert_border_right = self.vert_padding
                print(f"{self.vert_padding}{aligned_text}{self.vert_padding}")

        for line in subtext_lines:
            aligned_subtext = self.pc.apply_style(subtext_style, self.align_text(line, available_width, subtext_align))
            if self.vert_border:
                subtext_vert_border_left = self.vert_border + self.vert_padding if not subtext_vert_border_l_style else self.pc.apply_style(subtext_vert_border_l_style, self.vert_border) + self.vert_padding
                subtext_vert_border_right = self.vert_padding + self.vert_border if not subtext_vert_border_r_style else self.vert_padding + self.pc.apply_style(subtext_vert_border_r_style, self.vert_border)
                print(f"{subtext_vert_border_left}{aligned_subtext}{subtext_vert_border_right}")
            else:
                print(f"{self.vert_padding}{aligned_subtext}{self.vert_padding}")

        if horiz_border_bottom:
            horiz_border_bottom = self.horiz_border if not horiz_border_bottom_style else self.pc.apply_style(horiz_border_bottom_style, self.horiz_border)
            print(horiz_border_bottom)



    def print_border_boxed_text3(self, texts, text_styles=None, alignments=None,
                                 horiz_border_top=None, horiz_border_bottom=None,
                                 vert_border_left=None, vert_border_right=None,
                                 default_alignment='center'):

        # Set default values for parameters if not provided
        if not text_styles:
            text_styles = ['default'] * len(texts)
        if isinstance(text_styles, str):
            text_styles = [text_styles] * len(texts)

        if not alignments:
            alignments = [default_alignment] * len(texts)
        if isinstance(alignments, str):
            alignments = [alignments] * len(texts)

        available_width = self.get_available_width()
        lines_list = [self.split_text_to_lines(text, available_width) for text in texts]

        if horiz_border_top:
            print(horiz_border_top)

        for lines, text_style, text_align in zip(lines_list, text_styles, alignments):
            for line in lines:
                if line == 'invisible_text' or line == '':
                    line = ' '
                    aligned_text = self.align_text(line, available_width, text_align)
                else:
                    aligned_text = self.pc.apply_style(text_style, self.align_text(line, available_width, text_align))

                final_text = self.construct_text(vert_border_left, vert_border_right, aligned_text)

                print(final_text)

        if horiz_border_bottom:
            print(horiz_border_bottom)

    def print_border_boxed_text4(self, texts, text_styles=None, text_alignments=None,
                                 horiz_border_top=None, horiz_border_bottom=None,
                                 vert_border_left=None, vert_border_right=None,
                                 default_text_alignment='center',
                                 table_strs=None, table_strs_alignments=None,
                                 table_strs_horiz_border_top=False,
                                 table_strs_horiz_border_bottom=False,
                                 table_strs_vert_border_left=True,
                                 table_strs_vert_border_right=True,
                                 default_table_alignment='center',
                                 horiz_border_height=1):

        # Set default values for parameters if not provided
        if not text_styles:
            text_styles = ['default'] * len(texts)
        if isinstance(text_styles, str):
            text_styles = [text_styles] * len(texts)

        if not text_alignments:
            text_alignments = [default_text_alignment] * len(texts)
        if isinstance(text_alignments, str):
            text_alignments = [text_alignments] * len(texts)

        available_width = self.get_available_width()
        lines_list = [self.split_text_to_lines(text, available_width) for text in texts]

        if horiz_border_top:
            print(horiz_border_top * horiz_border_height)

        for lines, text_style, text_align in zip(lines_list, text_styles, text_alignments):
            for line in lines:
                if line == 'invisible_text' or line == '':
                    line = ' '
                    aligned_text = self.align_text(line, available_width, text_align)
                else:
                    aligned_text = self.pc.apply_style(text_style, self.align_text(line, available_width, text_align))

                final_text = self.construct_text(vert_border_left, vert_border_right, aligned_text)

                print(final_text)

        if horiz_border_bottom:
            print(horiz_border_bottom * horiz_border_height)
            blank_text = ' '.center(available_width)
            print(f'{vert_border_left}{blank_text}{vert_border_right}')


        if table_strs:
            if table_strs_horiz_border_top and isinstance(table_strs_horiz_border_top, bool):
                table_strs_horiz_border_top = horiz_border_top
            if table_strs_horiz_border_bottom and isinstance(table_strs_horiz_border_bottom, bool):
                table_strs_horiz_border_bottom = horiz_border_bottom
            if table_strs_vert_border_left and isinstance(table_strs_vert_border_left, bool):
                table_strs_vert_border_left = vert_border_left
            if table_strs_vert_border_right and isinstance(table_strs_vert_border_right, bool):
                table_strs_vert_border_right = vert_border_right


            if not table_strs_alignments:
                table_strs_alignments = [default_table_alignment] * len(table_strs)
            if isinstance(table_strs_alignments, str):
                table_strs_alignments = [table_strs_alignments] * len(table_strs)

            if len(table_strs) > 1:

                self.print_border_boxed_tables(table_strs,
                                               horiz_border_top=table_strs_horiz_border_top,
                                               vert_border_left=table_strs_vert_border_left,
                                               vert_border_right=table_strs_vert_border_right,
                                               horiz_border_bottom=table_strs_horiz_border_bottom,
                                               alignments=table_strs_alignments)
            else:
                table_str = table_strs[0]
                table_str_alignment = table_strs_alignments[0]
                self.print_border_boxed_table(table_str,
                                              table_strs_horiz_border_top,
                                              table_strs_vert_border_left,
                                              table_strs_vert_border_right,
                                              table_strs_horiz_border_bottom,
                                              text_align=table_str_alignment)

        if horiz_border_bottom:
            print(horiz_border_bottom)




    def print_border_boxed_table(self,
                                 table_str,
                                 horiz_border_top,
                                 vert_border_left,
                                 vert_border_right,
                                 horiz_border_bottom,
                                 table_style=None,
                                 text_style=None,
                                 text_align='center'):

        available_width = self.get_available_width()
        table_lines = table_str.split("\n")

        if horiz_border_top:
            print(horiz_border_top)
            blank_line = ' '.center(available_width)
            print(f'{vert_border_left}{blank_line}{vert_border_right}')

        for line in table_lines:
            stripped_line = self.strip_ansi_escape_sequences(line)
            padding_needed = available_width - len(stripped_line)
            if text_align == 'center':
                leading_spaces = padding_needed // 2
                trailing_spaces = padding_needed - leading_spaces
                aligned_text = ' ' * leading_spaces + line + ' ' * trailing_spaces
            elif text_align == 'left':
                aligned_text = line + ' ' * padding_needed
            else:
                aligned_text = padding_needed * ' ' + line


            final_text = self.construct_text(vert_border_left, vert_border_right, aligned_text)

            print(final_text)

            #print(f"{vert_border_left}{aligned_text}{vert_border_right}")
            #aligned_text = self.align_text(line, available_width, text_align)
            #print(f"{vert_border_left}{aligned_text}{vert_border_right}")

        if horiz_border_bottom:
            print(horiz_border_bottom)



    def print_border_boxed_tables(self,
                                  table_strs,
                                  horiz_border_top,
                                  vert_border_left,
                                  vert_border_right,
                                  horiz_border_bottom,
                                  table_padding=4,
                                  table_style=None,
                                  text_style=None,
                                  text_align='center',
                                  alignments=None):

        available_width = self.get_available_width()
        table_lines_list = [table_str.split("\n") for table_str in table_strs]

        blank_line = None

        max_lines = max(len(table_lines) for table_lines in table_lines_list)
        for table_lines in table_lines_list:
            table_lines += [''] * (max_lines - len(table_lines))

        if horiz_border_top:
            print(horiz_border_top)
            blank_line = ' '.center(available_width)
            print(f'{vert_border_left}{blank_line}{vert_border_right}')

        current_width = 0
        row_buffer = []

        for line_index in range(max_lines):
            row = ""
            row_length = 0
            for table_index, table_lines in enumerate(table_lines_list):
                line = table_lines[line_index]
                stripped_line = self.strip_ansi_escape_sequences(line)
                line_length = len(stripped_line)
                if current_width + line_length > available_width:
                    row_buffer.append(row.rstrip())
                    row = ""
                    current_width = 0
                if row:
                    row += " " * table_padding
                    row_length += table_padding
                row += line
                row_length += line_length
                current_width += line_length + table_padding

            if row:
                row_buffer.append(row.rstrip())
                current_width = 0

        for row in row_buffer:

            row_length = len(self.strip_ansi_escape_sequences(row))
            leading_spaces = (available_width - row_length) // 2
            if (available_width - row_length) % 2 != 0:
                leading_spaces += 1  # Adjust if the remaining space is odd
            #print(leading_spaces)
            #padding_needed = available_width - len(self.strip_ansi_escape_sequences(row))
            #aligned_text = row + ' ' * padding_needed
            aligned_text = ' ' * leading_spaces + row
            padding_needed = available_width - len(self.strip_ansi_escape_sequences(aligned_text))

            print(f"{vert_border_left}{aligned_text + ' ' * padding_needed}{vert_border_right}")



        if horiz_border_bottom:
            if not blank_line:
                blank_line = ' '.center(available_width) if vert_border_left and vert_border_right else ' '.center(self.horiz_width)
            print(f'{vert_border_left}{blank_line}{vert_border_right}')
            print(horiz_border_bottom)



    def print_border_boxed_tables2(self,
                                  table_strs,
                                  horiz_border_top,
                                  vert_border_left,
                                  vert_border_right,
                                  horiz_border_bottom,
                                  table_alignments=None,
                                  table_style=None,
                                  text_style=None):

        available_width = self.get_available_width()
        num_tables = len(table_strs)
        section_width = (available_width - (num_tables - 1)) // num_tables

        table_lines_list = [table_str.split("\n") for table_str in table_strs]
        max_lines = max(len(table_lines) for table_lines in table_lines_list)
        for table_lines in table_lines_list:
            table_lines += [''] * (max_lines - len(table_lines))

        if horiz_border_top:
            print(horiz_border_top)
            blank_line = ' '.center(available_width)
            print(f'{vert_border_left}{blank_line}{vert_border_right}')

        for line_index in range(max_lines):
            row = ""
            for table_index, table_lines in enumerate(table_lines_list):
                line = table_lines[line_index]
                stripped_line = self.strip_ansi_escape_sequences(line)
                padding_needed = section_width - len(stripped_line)
                if table_alignments and table_index < len(table_alignments):
                    text_align = table_alignments[table_index]
                else:
                    text_align = 'left'
                if text_align == 'center':
                    leading_spaces = padding_needed // 2
                    trailing_spaces = padding_needed - leading_spaces
                    aligned_line = ' ' * leading_spaces + line + ' ' * trailing_spaces
                elif text_align == 'left':
                    aligned_line = line + ' ' * padding_needed
                else:  # right align
                    aligned_line = ' ' * padding_needed + line
                if table_index > 0:
                    row += " "  # Padding between tables
                row += aligned_line
            row_length = len(self.strip_ansi_escape_sequences(row))
            padding_needed = available_width - row_length
            print(f"{vert_border_left}{row + ' ' * padding_needed}{vert_border_right}")

        if horiz_border_bottom:
            print(horiz_border_bottom)


    def print_border_boxed_tables4(self,
                                  table_strs,
                                  horiz_border_top,
                                  vert_border_left,
                                  vert_border_right,
                                  horiz_border_bottom,
                                  table_alignments=None,
                                  table_padding=4,
                                  table_style=None,
                                  text_style=None):
        available_width = self.get_available_width()
        num_tables = len(table_strs)
        section_width = (available_width - (num_tables - 1) * table_padding) // num_tables

        table_lines_list = [table_str.split("\n") for table_str in table_strs]
        max_lines = max(len(table_lines) for table_lines in table_lines_list)
        for table_lines in table_lines_list:
            table_lines += [''] * (max_lines - len(table_lines))

        for line_index in range(max_lines):
            row_parts = []
            for table_index, table_lines in enumerate(table_lines_list):
                line = table_lines[line_index]
                stripped_line = self.strip_ansi_escape_sequences(line)
                if table_alignments and table_index < len(table_alignments):
                    text_align = table_alignments[table_index]
                else:
                    text_align = 'left'

                aligned_line = self.align_text(line, section_width, text_align)
                row_parts.append(aligned_line)

            row = (' ' * table_padding).join(row_parts)
            row_length = len(self.strip_ansi_escape_sequences(row))
            padding_needed = available_width - row_length
            print(f"{vert_border_left}{row.ljust(available_width)}{vert_border_right}")



    def print_multi_column_box(self, columns, col_widths, col_styles=None, col_alignments=None,
                               horiz_border_top=True, horiz_border_bottom=True,
                               vert_border_left=True, vert_border_right=True):
        if len(columns) != len(col_widths):
            raise ValueError("Number of columns and column widths must match.")

        if col_styles and len(col_styles) != len(columns):
            raise ValueError("Number of column styles must match number of columns.")

        if col_alignments and len(col_alignments) != len(columns):
            raise ValueError("Number of column alignments must match number of columns.")

        available_width = self.get_available_width()
        total_col_width = sum(col_widths)
        if total_col_width > available_width:
            raise ValueError("Total width of columns exceeds available width.")

        horiz_border = self.pc.apply_style('purple', self.horiz_border)
        vert_border = self.pc.apply_style('orange', self.vert_border) if self.vert_border else ''

        if horiz_border_top:
            print(horiz_border)

        # Split each column's text into lines
        col_lines = [self.split_text_to_lines(col, col_widths[i]) for i, col in enumerate(columns)]
        max_lines = max(len(lines) for lines in col_lines)

        # Print each row of columns
        for line_num in range(max_lines):
            row = []
            for col_num in range(len(columns)):
                col_style = col_styles[col_num] if col_styles else 'default'
                col_align = col_alignments[col_num] if col_alignments else 'center'
                if line_num < len(col_lines[col_num]):
                    line = col_lines[col_num][line_num]
                    aligned_text = self.pc.apply_style(col_style, self.align_text(line, col_widths[col_num], col_align))
                else:
                    aligned_text = self.pc.apply_style(col_style, ' ' * col_widths[col_num])
                row.append(aligned_text)
            if vert_border_left and vert_border_right:
                print(f"{vert_border}{' '.join(row)}{vert_border}")
            elif vert_border_left:
                print(f"{vert_border}{' '.join(row)}")
            elif vert_border_right:
                print(f"{' '.join(row)}{vert_border}")
            else:
                print(' '.join(row))

        if horiz_border_bottom:
            print(horiz_border)


    def print_multi_column_box2(self, columns, col_widths, col_styles=None, col_alignments=None,
                               horiz_border_top=True, horiz_border_bottom=True,
                               vert_border_left=True, vert_border_right=True, col_sep=None,
                                col_widths_percent=False):

        if not col_sep:
            col_sep = self.vert_char

        if len(columns) != len(col_widths):
            raise ValueError("Number of columns and column widths must match.")

        if col_styles and len(col_styles) != len(columns):
            raise ValueError("Number of column styles must match number of columns.")

        if col_alignments and len(col_alignments) != len(columns):
            raise ValueError("Number of column alignments must match number of columns.")

        available_width = self.get_available_width()
        #print(f'horiz_width: {self.horiz_width}')
        #print(f'available_width: {available_width}')
        #total_padding = sig_columns + len(self.vert_padding) * sig_columns
        #total_padding = sig_columns + len(self.vert_padding) * sig_columns + sig_columns
        #total_padding = sig_columns + len(self.vert_padding) * sig_columns + sig_columns
        num_columns = len(columns)
        sig_columns = num_columns - 1
        #total_padding = sig_columns * (len(self.vert_padding) + 2)
        total_padding = sig_columns * (len(self.vert_padding) * 3)
        #print(f'total_padding: {total_padding}')

        if col_widths_percent:
            # Convert percentages to absolute widths
            col_widths = [int(available_width * (w / 100)) if w != '' else '' for w in col_widths]


        if '' in col_widths:
            unspecified_index = col_widths.index('')
            specified_width = sum(col_widths[i] for i in range(len(col_widths)) if i != unspecified_index)
            #print(f'specified_width: {specified_width}')
            remaining_width = available_width - specified_width - total_padding
            #print(f'remaining_width: {remaining_width}')
            #col_widths[unspecified_index] = remaining_width - len(self.vert_padding) * 2
            col_widths[unspecified_index] = remaining_width

        total_col_width = sum(col_widths)
        #print(f'total_col_width: {total_col_width}')
        if total_col_width > available_width:
            raise ValueError("Total width of columns exceeds available width.")

        horiz_border = self.pc.apply_style('purple', self.horiz_border)
        vert_border = self.pc.apply_style('orange', self.vert_border) if self.vert_border else ''

        if horiz_border_top:
            print(horiz_border)

        # Split each column's text into lines
        col_lines = [self.split_text_to_lines_v2(col, col_widths[i]) for i, col in enumerate(columns)]
        max_lines = max(len(lines) for lines in col_lines)

        # Print each row of columns
        for line_num in range(max_lines):
            row = []
            for col_num in range(len(columns)):
                col_style = col_styles[col_num] if col_styles else 'default'
                col_align = col_alignments[col_num] if col_alignments else 'center'
                if line_num < len(col_lines[col_num]):
                    line = col_lines[col_num][line_num]
                    aligned_text = self.pc.apply_style(col_style, self.align_text(line, col_widths[col_num], col_align), fill_space=False)
                    #aligned_text = self.align_text(line, col_widths[col_num], col_align)
                    #styled_text = self.pc.apply_style(col_style, aligned_text.strip())
                    #final_text = styled_text + ' ' * (col_widths[col_num] - len(aligned_text.strip()))
                else:
                    aligned_text = self.pc.apply_style(col_style, ' ' * col_widths[col_num], fill_space=False)
                    #final_text = ' ' * col_widths[col_num]
                row.append(aligned_text)
                #row.append(final_text)
            row_text = f"{self.vert_padding}{col_sep}{self.vert_padding}".join(row)
            if vert_border_left and vert_border_right:
                print(f"{vert_border}{self.vert_padding}{row_text}{self.vert_padding}{vert_border}")
            elif vert_border_left:
                print(f"{vert_border}{self.vert_padding}{row_text}{self.vert_padding}")
            elif vert_border_right:
                print(f"{self.vert_padding}{row_text}{self.vert_padding}{vert_border}")
            else:
                print(f"{self.vert_padding}{row_text}{self.vert_padding}")

        if horiz_border_bottom:
            print(horiz_border)


    def print_multi_column_box3(self, columns, col_widths, col_styles=None, col_alignments=None,
                                horiz_border_top=True, horiz_border_bottom=True,
                                vert_border_left=True, vert_border_right=True, col_sep=None,
                                col_widths_percent=False):

        if not col_sep:
            col_sep = self.vert_char

        if len(columns) != len(col_widths):
            raise ValueError("Number of columns and column widths must match.")

        if col_styles and len(col_styles) != len(columns):
            raise ValueError("Number of column styles must match number of columns.")

        if col_alignments and len(col_alignments) != len(columns):
            raise ValueError("Number of column alignments must match number of columns.")

        available_width = self.get_available_width()
        #print(f'horiz_width: {self.horiz_width}')
        #print(f'available_width: {available_width}')
        num_columns = len(columns)
        sig_columns = num_columns - 1
        total_padding = sig_columns * (len(self.vert_padding) * 3)
        #print(f'total_padding: {total_padding}')

        if col_widths_percent:
            # Convert percentages to absolute widths
            col_widths = [int(available_width * (w / 100)) if w != '' else '' for w in col_widths]

        if '' in col_widths:
            unspecified_index = col_widths.index('')
            specified_width = sum(col_widths[i] for i in range(len(col_widths)) if i != unspecified_index and col_widths[i] != '')
            #print(f'specified_width: {specified_width}')
            remaining_width = available_width - specified_width - total_padding
            #print(f'remaining_width: {remaining_width}')
            col_widths[unspecified_index] = remaining_width

        total_col_width = sum(col_widths)
        #print(f'total_col_width: {total_col_width}')
        if total_col_width > available_width:
            raise ValueError("Total width of columns exceeds available width.")

        horiz_border = self.pc.apply_style('purple', self.horiz_border)
        vert_border = self.pc.apply_style('orange', self.vert_border) if self.vert_border else ''

        if horiz_border_top:
            print(horiz_border)

        # Split each column's text into lines
        col_lines = [self.split_text_to_lines_v2(col, col_widths[i]) for i, col in enumerate(columns)]
        max_lines = max(len(lines) for lines in col_lines)

        # Print each row of columns
        for line_num in range(max_lines):
            row = []
            for col_num in range(len(columns)):
                col_style = col_styles[col_num] if col_styles else 'default'
                col_align = col_alignments[col_num] if col_alignments else 'center'
                if line_num < len(col_lines[col_num]):
                    line = col_lines[col_num][line_num]
                    aligned_text = self.pc.apply_style(col_style, self.align_text(line, col_widths[col_num], col_align), fill_space=False)
                else:
                    aligned_text = self.pc.apply_style(col_style, ' ' * col_widths[col_num], fill_space=False)
                row.append(aligned_text)
            row_text = f"{self.vert_padding}{col_sep}{self.vert_padding}".join(row)
            if vert_border_left and vert_border_right:
                print(f"{vert_border}{self.vert_padding}{row_text}{self.vert_padding}{vert_border}")
            elif vert_border_left:
                print(f"{vert_border}{self.vert_padding}{row_text}{self.vert_padding}")
            elif vert_border_right:
                print(f"{self.vert_padding}{row_text}{self.vert_padding}{vert_border}")
            else:
                print(f"{self.vert_padding}{row_text}{self.vert_padding}")

        if horiz_border_bottom:
            print(horiz_border)


    def print_multi_column_box4(self, columns, col_widths, col_styles=None, col_alignments=None,
                                horiz_border_top=True, horiz_border_bottom=True,
                                vert_border_left=True, vert_border_right=True, col_sep=None,
                                col_sep_width=1):

        if not col_sep:
            col_sep = self.vert_char

        if len(columns) != len(col_widths):
            raise ValueError("Number of columns and column widths must match.")

        if col_styles and len(col_styles) != len(columns):
            raise ValueError("Number of column styles must match number of columns.")

        if col_alignments and len(col_alignments) != len(columns):
            raise ValueError("Number of column alignments must match number of columns.")

        available_width = self.get_available_width()
        #print(f'horiz_width: {self.horiz_width}')
        #print(f'available_width: {available_width}')

        num_columns = len(columns)
        sig_columns = num_columns - 1
        col_sep_length = len(col_sep) * col_sep_width
        col_sep = col_sep * col_sep_width
        #total_padding = (sig_columns * col_sep_length) * (len(self.vert_padding) * 3)
        total_padding = (sig_columns * len(col_sep) * (len(self.vert_padding) * 2))
        #print(f'total_padding: {total_padding}')

        if '' in col_widths:
            unspecified_index = col_widths.index('')
            specified_width = sum(col_widths[i] for i in range(len(col_widths)) if i != unspecified_index)
            #print(f'specified_width: {specified_width}')
            remaining_width = available_width - specified_width - total_padding
            #print(f'remaining_width: {remaining_width}')
            col_widths[unspecified_index] = remaining_width

        total_col_width = sum(col_widths)
        #print(f'total_col_width: {total_col_width}')
        if total_col_width > available_width:
            raise ValueError("Total width of columns exceeds available width.")

        horiz_border = self.pc.apply_style('purple', self.horiz_border)
        vert_border = self.pc.apply_style('orange', self.vert_border) if self.vert_border else ''

        if horiz_border_top:
            print(horiz_border)

        col_lines = [self.split_text_to_lines_v2(col, col_widths[i]) for i, col in enumerate(columns)]
        max_lines = max(len(lines) for lines in col_lines)

        for line_num in range(max_lines):
            row = []
            for col_num in range(len(columns)):
                col_style = col_styles[col_num] if col_styles else 'default'
                col_align = col_alignments[col_num] if col_alignments else 'center'
                if line_num < len(col_lines[col_num]):
                    line = col_lines[col_num][line_num]
                    aligned_text = self.pc.apply_style(col_style, self.align_text(line, col_widths[col_num], col_align), fill_space=False)
                else:
                    aligned_text = self.pc.apply_style(col_style, ' ' * col_widths[col_num], fill_space=False)
                row.append(aligned_text)
            row_text = f"{self.vert_padding}{col_sep * col_sep_width}{self.vert_padding}".join(row)
            if vert_border_left and vert_border_right:
                print(f"{vert_border}{self.vert_padding}{row_text}{self.vert_padding}{vert_border}")
            elif vert_border_left:
                print(f"{vert_border}{self.vert_padding}{row_text}{self.vert_padding}")
            elif vert_border_right:
                print(f"{self.vert_padding}{row_text}{self.vert_padding}{vert_border}")
            else:
                print(f"{self.vert_padding}{row_text}{self.vert_padding}")

        if horiz_border_bottom:
            print(horiz_border)
