# frame_builder.py

from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from .prints_charming import PrintsCharming



class FrameBuilder:

    def __init__(self, pc=None, horiz_width=None, horiz_char=' ', vert_width=2, vert_padding=1, vert_char='|', inner_char='|', inner_width=2, inner_padding=1, ansi_escape_pattern='sgr_strict'):
        if isinstance(pc, str):
            self.pc = PrintsCharming.get_shared_instance(pc)
            if not self.pc:
                self.pc = PrintsCharming()
                self.pc.warning(f"No shared instance found for key '{pc}'. Using a new instance with default init.")
        else:
            self.pc = pc or PrintsCharming()
        self.terminal_width = self.pc.terminal_width
        self.terminal_height = self.pc.terminal_height
        self.horiz_width = horiz_width if horiz_width else self.terminal_width
        self.horiz_char = horiz_char
        self.horiz_border = self.horiz_width * horiz_char
        self.vert_width = vert_width
        self.vert_padding = vert_padding * ' '
        self.vert_char = horiz_char if vert_width and not vert_char else vert_char
        self.inner_char = inner_char
        self.inner_width = inner_width
        self.inner_padding = inner_padding * ' '
        self.ansi_escape_pattern = (
            self.pc.__class__.ansi_escape_patterns.get(ansi_escape_pattern)
        )
        self.vert_border = '' if not vert_width else vert_width * self.vert_char
        self.inner_border = '' if not inner_width else inner_width * self.inner_char
        self.available_width = None

        self.top_border_height = 1
        self.bottom_border_height = 1
        self.horiz_border_height = 1

        self.nested_widths = {}

        self.frames = {}
        self.previous_values = {}




    def generate_frame(self,
                       frame_name: Optional[str] = None,
                       texts: List[str] = None,
                       text_styles: Union[str, List[str]] = None,
                       text_alignments: Union[str, List[str]] = 'center',
                       horiz_border_top: bool = True,
                       horiz_border_top_style: Optional[str] = None,
                       horiz_border_bottom: bool = True,
                       horiz_border_bottom_style: Optional[str] = None,
                       vert_border_left: bool = True,
                       vert_border_left_style: Optional[str] = None,
                       vert_border_inner: bool = False,
                       vert_border_inner_style: Optional[str] = None,
                       vert_border_right: bool = True,
                       vert_border_right_style: Optional[str] = None,
                       default_text_alignment: str = 'center',
                       table_strs: Optional[List[str]] = None,
                       table_strs_alignments: Union[str, List[str]] = 'center',
                       ephemeral: bool = False,
                       append_newline: bool = False,
                       **kwargs) -> str:
        """
        Generates a frame with optional styling and alignment as a string.

        :param frame_name: The name of the frame (used for storage and reference).
        :param texts: A list of strings to be included in the frame.
        :param text_styles: Style(s) to apply to the texts.
        :param text_alignments: Alignment(s) for the texts.
        :param horiz_border_top: Whether to display the top horizontal border.
        :param horiz_border_top_style: Style for the top horizontal border.
        :param horiz_border_bottom: Whether to display the bottom horizontal border.
        :param horiz_border_bottom_style: Style for the bottom horizontal border.
        :param vert_border_left: Whether to display the left vertical border.
        :param vert_border_left_style: Style for the left vertical border.
        :param vert_border_inner: Whether to display an inner vertical border.
        :param vert_border_inner_style: Style for the inner vertical border.
        :param vert_border_right: Whether to display the right vertical border.
        :param vert_border_right_style: Style for the right vertical border.
        :param default_text_alignment: Default text alignment if not specified.
        :param table_strs: List of table strings to include in the frame.
        :param table_strs_alignments: Alignment(s) for the table strings.
        :param ephemeral: If True, the frame is not stored for future updates.
        :param append_newline: If True, adds a newline character at the end of the frame string.
        :return: A string representing the formatted frame.
        """

        # Build the styled borders
        horiz_border_top_str, vert_border_left_str, vert_border_inner_str, vert_border_right_str, horiz_border_bottom_str = self.build_styled_border_box(
            border_top=horiz_border_top,
            border_top_style=horiz_border_top_style,
            border_bottom=horiz_border_bottom,
            border_bottom_style=horiz_border_bottom_style,
            border_left=vert_border_left,
            border_left_style=vert_border_left_style,
            border_inner=vert_border_inner,
            border_inner_style=vert_border_inner_style,
            border_right=vert_border_right,
            border_right_style=vert_border_right_style
        )

        # Prepare the frame output
        frame_lines = []

        if horiz_border_top_str:
            frame_lines.append(horiz_border_top_str)

        # Process the texts
        if texts:
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

            for lines, text_style, text_align in zip(lines_list, text_styles, text_alignments):
                for line in lines:
                    if line == 'invisible_text' or line == '':
                        line = ' '
                        aligned_text = self.align_text(line, available_width, text_align)
                    else:
                        aligned_text = self.pc.apply_style(text_style, self.align_text(line, available_width, text_align))

                    final_text = self.construct_text(vert_border_left_str, vert_border_right_str, aligned_text)
                    frame_lines.append(final_text)

        # Process the tables if any
        if table_strs:
            if isinstance(table_strs_alignments, str):
                table_strs_alignments = [table_strs_alignments] * len(table_strs)

            for table_str, table_align in zip(table_strs, table_strs_alignments):
                table_lines = table_str.split("\n")
                for line in table_lines:
                    stripped_line = self.strip_ansi_escape_sequences(line)
                    padding_needed = self.get_available_width() - len(stripped_line)
                    if table_align == 'center':
                        leading_spaces = padding_needed // 2
                        trailing_spaces = padding_needed - leading_spaces
                        aligned_text = ' ' * leading_spaces + line + ' ' * trailing_spaces
                    elif table_align == 'left':
                        aligned_text = line + ' ' * padding_needed
                    else:
                        aligned_text = ' ' * padding_needed + line

                    final_text = self.construct_text(vert_border_left_str, vert_border_right_str, aligned_text)
                    frame_lines.append(final_text)

        if horiz_border_bottom_str:
            frame_lines.append(horiz_border_bottom_str)

        # Combine lines into a single string
        frame_str = "\n".join(frame_lines)

        # Append newline if parameter is True
        if append_newline:
            frame_str += "\n"

        # Check if the frame should be stored
        if frame_name and not ephemeral:
            self.frames[frame_name] = {
                "texts": texts,
                "frame_content": frame_str,
                "format_params": {
                    "text_styles": text_styles,
                    "text_alignments": text_alignments,
                    "horiz_border_top": horiz_border_top,
                    "horiz_border_top_style": horiz_border_top_style,
                    "horiz_border_bottom": horiz_border_bottom,
                    "horiz_border_bottom_style": horiz_border_bottom_style,
                    "vert_border_left": vert_border_left,
                    "vert_border_left_style": vert_border_left_style,
                    "vert_border_right": vert_border_right,
                    "vert_border_right_style": vert_border_right_style,
                    "default_text_alignment": default_text_alignment,
                    "table_strs": table_strs,
                    "table_strs_alignments": table_strs_alignments,
                    **kwargs
                }
            }

        return frame_str


    def refresh_frame(self, frame_name: str, new_texts: Optional[List[str]] = None) -> None:
        """
        Refreshes a stored frame by updating its content.

        :param frame_name: The name of the frame to refresh.
        :param new_texts: New texts to update the frame with.
        """
        if frame_name not in self.frames:
            raise ValueError(f"Frame '{frame_name}' does not exist.")

        frame_info = self.frames[frame_name]
        format_params = frame_info["format_params"]

        # Update texts if new_texts is provided
        texts = new_texts if new_texts else frame_info["texts"]

        # Re-generate the frame
        frame_str = self.generate_frame(
            frame_name=frame_name,
            texts=texts,
            ephemeral=True,
            **format_params
        )

        # Update the stored frame content
        self.frames[frame_name]["frame_content"] = frame_str

        # Move cursor to the starting position of the frame
        # This assumes you have stored the starting line when you first printed the frame
        # For simplicity, we'll just print the updated frame
        print(frame_str, flush=True)


    def get_frame(self, frame_name: str) -> str:
        """
        Retrieves the stored frame content.

        :param frame_name: The name of the frame to retrieve.
        :return: The frame content as a string.
        """
        if frame_name not in self.frames:
            raise ValueError(f"Frame '{frame_name}' does not exist.")

        return self.frames[frame_name]["frame_content"]


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


    def align_text(self, text, available_width=None, align='center'):
        if not available_width:
            available_width = self.get_available_width()

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



    def split_text_to_lines(self, text, available_width, preserve_newlines=True):
        lines = text.split('\n') if preserve_newlines else [text]
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


    def get_available_width(self, num_inner_borders=0):
        if self.available_width is None:
            self.available_width = (
                self.horiz_width - (2 * self.vert_width) - (len(self.vert_padding) * 2)
                if self.vert_border
                else self.horiz_width - (len(self.vert_padding) * 2)
            )

        # Deduct space for the specified number of inner borders and their padding
        additional_border_space = num_inner_borders * (self.inner_width + (2 * len(self.inner_padding)))
        #print(f'additional_border_space: {additional_border_space}')

        return self.available_width - additional_border_space


    def get_available_nested_width(self, level, num_inner_borders=0):
        if level == 1:
            level += 1

        unnested_available_width = self.get_available_width(num_inner_borders=num_inner_borders)

        return unnested_available_width - self.available_width




    def strip_ansi_escape_sequences(self, text):
        return self.ansi_escape_pattern.sub('', text)


    def build_unstyled_border_box(self, level=1):
        border_top = self.horiz_border
        border_left = self.vert_border + self.vert_padding
        border_inner = self.inner_padding + self.inner_border + self.inner_padding if self.inner_border else ''
        border_right = self.vert_padding + self.vert_border
        border_bottom = self.horiz_border

        return border_top, border_left, border_inner, border_right, border_bottom


    def build_styled_border_box(self, style=None, horiz_style=None, vert_style=None,
                                border_top=True, border_top_style=None,
                                border_bottom=True, border_bottom_style=None,
                                border_left=True, border_left_style=None,
                                border_inner=True, border_inner_style=None,
                                border_right=True, border_right_style=None,
                                width=100):

        # Apply top border style
        if border_top:
            top_style = border_top_style or horiz_style or style
            horiz_border_top = self.horiz_border if not top_style else self.pc.apply_style(top_style, self.horiz_border)
        else:
            horiz_border_top = None

        # Apply bottom border style
        if border_bottom:
            bottom_style = border_bottom_style or horiz_style or style
            horiz_border_bottom = self.horiz_border if not bottom_style else self.pc.apply_style(bottom_style, self.horiz_border)
        else:
            horiz_border_bottom = None

        # Apply left border style
        if border_left:
            left_style = border_left_style or vert_style or style
            vert_border_left = (self.vert_border + self.vert_padding if not left_style
                                else self.pc.apply_style(left_style, self.vert_border) + self.vert_padding)
        else:
            vert_border_left = self.vert_padding

        # Apply right border style
        if border_right:
            right_style = border_right_style or vert_style or style
            vert_border_right = (self.vert_padding + self.vert_border if not right_style
                                 else self.vert_padding + self.pc.apply_style(right_style, self.vert_border))
        else:
            vert_border_right = self.vert_padding

        # Apply inner border style with padding on both sides
        if border_inner:
            inner_style = border_inner_style or vert_style or style
            if isinstance(border_inner, str):
                vert_border_inner = (self.inner_padding + border_inner + self.inner_padding if not inner_style
                                     else self.inner_padding + self.pc.apply_style(inner_style, border_inner) + self.inner_padding)
            else:
                vert_border_inner = (self.inner_padding + self.inner_border + self.inner_padding if not inner_style
                                     else self.inner_padding + self.pc.apply_style(inner_style, self.inner_border) + self.inner_padding)

        else:
            vert_border_inner = None

        return horiz_border_top, vert_border_left, vert_border_inner, vert_border_right, horiz_border_bottom




    def print_border_boxed_text22(self, texts, text_styles=None, alignments=None,
                                 style=None, horiz_style=None, vert_style=None,
                                 blank_top_line=False, blank_bottom_line=False,
                                 border_top=True, border_bottom=True, border_left=True, border_right=True,
                                 border_inner=True,
                                 border_top_style=None, border_bottom_style=None,
                                 border_left_style=None, border_right_style=None,
                                 border_inner_style=None,
                                 match_column_heights=True):
        """
        Print a border-boxed text layout with optional text-wrapping, and a new parameter `match_column_heights`.
        If match_column_heights=True (default), columns in a row will align at the bottom, possibly adding blank lines to shorter columns.
        If match_column_heights=False, each column is printed only as many lines as it needs, and then gets its bottom border. Columns may end at different heights.
        """

        (horiz_border_top,
         vert_border_left,
         vert_border_inner,
         vert_border_right,
         horiz_border_bottom) = self.build_styled_border_box(
            style=style,
            horiz_style=horiz_style,
            vert_style=vert_style,
            border_top=border_top,
            border_top_style=border_top_style,
            border_bottom=border_bottom,
            border_bottom_style=border_bottom_style,
            border_left=border_left,
            border_left_style=border_left_style,
            border_right=border_right,
            border_right_style=border_right_style,
            border_inner=border_inner,
            border_inner_style=border_inner_style
        )

        # horiz_border_inner is used for empty rows, or potentially between rows
        horiz_border_inner = horiz_border_bottom

        # Normalize texts into list-of-lists
        normalized_texts = []
        for row in texts:
            if isinstance(row, list):
                normalized_texts.append(row)
            else:
                normalized_texts.append([row])

        # Normalize text_styles
        if not text_styles:
            text_styles = [['default'] * len(row) for row in normalized_texts]
        elif isinstance(text_styles, str):
            text_styles = [[text_styles] * len(row) for row in normalized_texts]
        else:
            expanded_text_styles = []
            for idx, row in enumerate(normalized_texts):
                if idx < len(text_styles):
                    row_styles = text_styles[idx]
                    if isinstance(row_styles, str):
                        expanded_text_styles.append([row_styles] * len(row))
                    else:
                        expanded_text_styles.append(row_styles)
                else:
                    expanded_text_styles.append(['default'] * len(row))
            text_styles = expanded_text_styles

        # Normalize alignments
        if not alignments:
            alignments = [['center'] * len(row) for row in normalized_texts]
        elif isinstance(alignments, str):
            alignments = [[alignments] * len(row) for row in normalized_texts]
        else:
            expanded_alignments = []
            for idx, row in enumerate(normalized_texts):
                if idx < len(alignments):
                    row_alignments = alignments[idx]
                    if isinstance(row_alignments, str):
                        expanded_alignments.append([row_alignments] * len(row))
                    else:
                        expanded_alignments.append(row_alignments)
                else:
                    expanded_alignments.append(['center'] * len(row))
            alignments = expanded_alignments

        # Print top border if requested
        if border_top:
            print(horiz_border_top)
            if blank_top_line:
                num_inner_borders = max((len(row) - 1) for row in normalized_texts if row)
                available_width = self.get_available_width(num_inner_borders=num_inner_borders)
                blank_text = ' '.center(available_width)
                left_border = vert_border_left if vert_border_left else ''
                right_border = vert_border_right if vert_border_right else ''
                print(f'{left_border}{blank_text}{right_border}')

        for row_idx, (row_texts, row_styles, row_aligns) in enumerate(zip(normalized_texts, text_styles, alignments)):
            if not row_texts:
                # Empty row: print horizontal inner border
                print(horiz_border_inner)
                continue

            num_columns = len(row_texts)
            num_inner_borders = (num_columns - 1) if num_columns > 1 else 0
            available_width = self.get_available_width(num_inner_borders=num_inner_borders)

            # Compute column widths
            section_width = available_width // num_columns
            leftover_space = available_width - (section_width * num_columns)
            column_widths = [section_width] * num_columns
            for i in range(leftover_space):
                column_widths[-(i + 1)] += 1

            # Split columns into multiple lines
            splitted_columns = []
            for col_idx, (text, style, align) in enumerate(zip(row_texts, row_styles, row_aligns)):
                column_lines = self.split_text_to_lines(text, column_widths[col_idx])
                if not column_lines:
                    column_lines = [' ']
                splitted_columns.append({
                    'lines': column_lines,
                    'style': style,
                    'align': align,
                    'width': column_widths[col_idx],
                    'closed': False  # To track when this column has printed bottom border
                })

            if match_column_heights:
                # Original behavior: Match all columns to the same number of lines
                max_lines = max(len(col['lines']) for col in splitted_columns)
                for line_idx in range(max_lines):
                    line_fragments = []
                    for col in splitted_columns:
                        line_text = col['lines'][line_idx] if line_idx < len(col['lines']) else ' '
                        aligned_text = self.align_text(line_text, align=col['align'], available_width=col['width'])
                        styled_text = self.pc.apply_style(col['style'], aligned_text)
                        line_fragments.append(styled_text)
                    left_border = vert_border_left if vert_border_left else ''
                    right_border = vert_border_right if vert_border_right else ''
                    inner_border = vert_border_inner if vert_border_inner else ''
                    full_line = left_border + inner_border.join(line_fragments) + right_border
                    print(full_line)
            else:
                # New behavior: Each column prints its own lines and ends when done.
                # We iterate line by line, but columns may run out of lines at different times.
                # Once a column is done, we print its bottom border segment and mark it as closed.

                # We'll keep iterating until all columns are closed.
                while not all(col['closed'] for col in splitted_columns):
                    line_fragments = []
                    # Construct the line for the current iteration
                    any_column_printed = False
                    for col in splitted_columns:
                        if col['closed']:
                            # This column is already closed, print nothing for it
                            # You could choose to print spaces or skip entirely.
                            # But since columns are side-by-side, we must consider how to handle closed columns.
                            # Here, we will simply print a border segment if needed or just a space.
                            # In reality, once closed, that column segment should probably disappear.
                            # Let's just put a minimal space or possibly omit it. But omitting breaks alignment.
                            # Since the user wants independent column heights, we may represent a closed column as a vertical border line (left/right)
                            # Here, let's keep a vertical border and fill with spaces, no inner border.
                            # This is ambiguous as a design choice.
                            # We'll represent a closed column as just its vertical borders with a blank space inside.
                            aligned_text = ' ' * col['width']
                            styled_text = aligned_text  # no styling needed since column is closed
                            line_fragments.append(styled_text)
                        else:
                            # Column still has lines to print
                            if col['lines']:
                                line_text = col['lines'].pop(0)  # get the next line
                                aligned_text = self.align_text(line_text, align=col['align'], available_width=col['width'])
                                styled_text = self.pc.apply_style(col['style'], aligned_text)
                                line_fragments.append(styled_text)
                                any_column_printed = True
                            else:
                                # No more lines left for this column, print bottom border line
                                # The column is now considered closed. We'll print a horizontal line segment for this column.
                                # Actually, since we are printing line by line, to "close" the column, we should print a horizontal
                                # border line here. But that border line is usually printed at the bottom after all lines.
                                # For independent column closure, let's print a line composed of the horizontal border character.
                                # We'll then mark the column as closed.
                                horizontal_char = horiz_border_bottom.strip('\n')  # The bottom border might be full length line
                                # We need a segment of the bottom border that matches this column width + borders
                                # Since horiz_border_bottom is typically a full line, we need to slice it.
                                # If building partial segments is complex, we might consider a simpler approach:
                                #   Just mark closed and assume final border printed after loop ends for that column.
                                # However, user wants the bottom border right after the column finishes.
                                # Let's assume build_styled_border_box gives consistent patterns.
                                # We'll approximate by using the horizontal line character (like '─') repeated for column width.
                                # The border chars are typically single or double line chars. Let's deduce them.

                                # If horiz_border_bottom contains something like left corner, line chars, then right corner,
                                # we can extract a portion that corresponds to this column's width. For simplicity, let's assume
                                # a simple character repetition. If needed, we can store a horizontal char pattern from build_styled_border_box.

                                # For a robust approach, let's assume horiz_border_bottom is something like:
                                # "└───┴───┘"
                                # We need a segment that equals the column width plus appropriate border segments.
                                # Since this code is complex, let's simplify by using a line of horizontal chars:
                                horizontal_line_char = ' '  # or use '-'
                                bottom_segment = horizontal_line_char * col['width']
                                # Apply style from bottom border if available
                                bottom_styled = self.pc.apply_style('bottom_segment', bottom_segment)
                                line_fragments.append(bottom_styled)
                                col['closed'] = True

                    # If no column printed a text line and some got closed, we still print the constructed line
                    # If all columns are closed after this iteration, the loop ends anyway.
                    if any_column_printed or any(not c['closed'] for c in splitted_columns):
                        left_border = vert_border_left if vert_border_left else ''
                        right_border = vert_border_right if vert_border_right else ''
                        inner_border = vert_border_inner if vert_border_inner else ''
                        full_line = left_border + inner_border.join(line_fragments) + right_border
                        print(full_line)

            # After finishing all lines for this row under match_column_heights=True,
            # or after the loop for match_column_heights=False, we do nothing special here.
            # The bottom border for the row will be printed after all rows, unless blank_bottom_line is requested.

        # Print bottom border if requested
        if border_bottom:
            if blank_bottom_line:
                num_inner_borders = max((len(row) - 1) for row in normalized_texts if row)
                available_width = self.get_available_width(num_inner_borders=num_inner_borders)
                blank_text = ' '.center(available_width)
                left_border = vert_border_left if vert_border_left else ''
                right_border = vert_border_right if vert_border_right else ''
                print(f'{left_border}{blank_text}{right_border}')
            print(horiz_border_bottom)

    def print_border_boxed_text2(self, texts, text_styles=None, alignments=None,
                                 style=None, horiz_style=None, vert_style=None,
                                 blank_top_line=False, blank_bottom_line=False,
                                 border_top=True, border_bottom=True, border_left=True, border_right=True,
                                 border_inner=True,
                                 border_top_style=None, border_bottom_style=None,
                                 border_left_style=None, border_right_style=None,
                                 border_inner_style=None):

        # Build borders using build_styled_border_box
        (horiz_border_top,
         vert_border_left,
         vert_border_inner,
         vert_border_right,
         horiz_border_bottom) = self.build_styled_border_box(
            style=style,
            horiz_style=horiz_style,
            vert_style=vert_style,
            border_top=border_top,
            border_top_style=border_top_style,
            border_bottom=border_bottom,
            border_bottom_style=border_bottom_style,
            border_left=border_left,
            border_left_style=border_left_style,
            border_right=border_right,
            border_right_style=border_right_style,
            border_inner=border_inner,
            border_inner_style=border_inner_style
        )

        # For horizontal inner border, you might need to adjust or build it accordingly
        horiz_border_inner = horiz_border_bottom

        # Normalize texts to be a list of rows, each row is a list of column texts
        normalized_texts = []
        for row in texts:
            if isinstance(row, list):
                normalized_texts.append(row)
            else:
                normalized_texts.append([row])

        num_rows = len(normalized_texts)

        # Normalize text_styles
        if not text_styles:
            text_styles = [['default'] * len(row) for row in normalized_texts]
        elif isinstance(text_styles, str):
            text_styles = [[text_styles] * len(row) for row in normalized_texts]
        else:
            # Expand text_styles to match normalized_texts dimensions
            expanded_text_styles = []
            text_styles_len = len(text_styles)
            for idx, row in enumerate(normalized_texts):
                if idx < text_styles_len:
                    row_styles = text_styles[idx]
                    if isinstance(row_styles, str):
                        # same style for all columns
                        expanded_text_styles.append([row_styles] * len(row))
                    else:
                        expanded_text_styles.append(row_styles)
                else:
                    expanded_text_styles.append(['default'] * len(row))
            text_styles = expanded_text_styles

        # Normalize alignments
        if not alignments:
            alignments = [['center'] * len(row) for row in normalized_texts]
        elif isinstance(alignments, str):
            alignments = [[alignments] * len(row) for row in normalized_texts]
        else:
            # Expand alignments to match normalized_texts
            expanded_alignments = []
            alignments_len = len(alignments)
            for idx, row in enumerate(normalized_texts):
                if idx < alignments_len:
                    row_alignments = alignments[idx]
                    if isinstance(row_alignments, str):
                        expanded_alignments.append([row_alignments] * len(row))
                    else:
                        expanded_alignments.append(row_alignments)
                else:
                    expanded_alignments.append(['center'] * len(row))
            alignments = expanded_alignments

        # Print top border if any
        if border_top:
            print(horiz_border_top)
            if blank_top_line:
                num_inner_borders = max((len(row) - 1) for row in normalized_texts if row)
                available_width = self.get_available_width(num_inner_borders=num_inner_borders)
                blank_text = ' '.center(available_width)
                left_border = vert_border_left if vert_border_left else ''
                right_border = vert_border_right if vert_border_right else ''
                print(f'{left_border}{blank_text}{right_border}')

        # Iterate over each row of texts
        for row_idx, (row_texts, row_styles, row_aligns) in enumerate(zip(normalized_texts, text_styles, alignments)):
            if not row_texts:  # empty row -> print horizontal inner border
                print(horiz_border_inner)
                continue

            num_columns = len(row_texts)
            num_inner_borders = num_columns - 1 if num_columns > 1 else 0

            # Compute total available width for the entire line
            available_width = self.get_available_width(num_inner_borders=num_inner_borders)

            # Determine individual column widths
            section_width = available_width // num_columns
            leftover_space = available_width - (section_width * num_columns)
            column_widths = [section_width] * num_columns
            for i in range(leftover_space):
                column_widths[-(i + 1)] += 1

            # For each column text, we must now split it into multiple lines
            # according to its column width. Each column will produce a list of lines.
            splitted_columns = []
            for col_idx, (text, style, align) in enumerate(zip(row_texts, row_styles, row_aligns)):
                # Split text into multiple lines fitting column_widths[col_idx]
                column_lines = self.split_text_to_lines(text, column_widths[col_idx])

                # If text is empty or special 'invisible_text', handle gracefully
                if not column_lines:
                    column_lines = [' ']

                # Store these lines along with style and alignment info for later printing
                splitted_columns.append((column_lines, style, align))

            # Determine how many lines we need to print for this row
            # (the max number of lines among the columns)
            max_lines = max(len(col[0]) for col in splitted_columns)

            # Print each line by iterating through all columns line by line
            for line_index in range(max_lines):
                column_line_fragments = []
                for (column_lines, style, align), width in zip(splitted_columns, column_widths):
                    # Retrieve the appropriate line if it exists, else use blank
                    line_text = column_lines[line_index] if line_index < len(column_lines) else ' '

                    # Align and style the text
                    aligned_text = self.align_text(line_text, align=align, available_width=width)
                    styled_text = self.pc.apply_style(style, aligned_text)
                    column_line_fragments.append(styled_text)

                # Construct full line with borders and inner borders
                left_border = vert_border_left if vert_border_left else ''
                right_border = vert_border_right if vert_border_right else ''
                inner_border = vert_border_inner if vert_border_inner else ''
                full_line = left_border + inner_border.join(column_line_fragments) + right_border

                print(full_line)

            # After finishing all lines for this row, if not last row, print horiz_border_inner
            # if that's desired (this depends on your existing logic).
            # Since this code was originally repeating the bottom border at the end,
            # we might leave horizontal inner borders for rows with no text.
            # However, in the original code, horiz_border_inner is only printed on empty rows,
            # so we won't print it here unless needed.

        # Print bottom border if any
        if border_bottom:
            if blank_bottom_line:
                num_inner_borders = max((len(row) - 1) for row in normalized_texts if row)
                available_width = self.get_available_width(num_inner_borders=num_inner_borders)
                blank_text = ' '.center(available_width)
                left_border = vert_border_left if vert_border_left else ''
                right_border = vert_border_right if vert_border_right else ''
                print(f'{left_border}{blank_text}{right_border}')
            print(horiz_border_bottom)

    def print_border_boxed_text1(self, texts, text_styles=None, alignments=None,
                                style=None, horiz_style=None, vert_style=None,
                                blank_top_line=False, blank_bottom_line=False,
                                border_top=True, border_bottom=True, border_left=True, border_right=True,
                                border_inner=True,
                                border_top_style=None, border_bottom_style=None,
                                border_left_style=None, border_right_style=None,
                                border_inner_style=None):

        # Build borders using build_styled_border_box
        (horiz_border_top,
         vert_border_left,
         vert_border_inner,
         vert_border_right,
         horiz_border_bottom) = self.build_styled_border_box(
            style=style,
            horiz_style=horiz_style,
            vert_style=vert_style,
            border_top=border_top,
            border_top_style=border_top_style,
            border_bottom=border_bottom,
            border_bottom_style=border_bottom_style,
            border_left=border_left,
            border_left_style=border_left_style,
            border_right=border_right,
            border_right_style=border_right_style,
            border_inner=border_inner,
            border_inner_style=border_inner_style
        )

        # For horizontal inner border, you might need to adjust or build it accordingly
        horiz_border_inner = horiz_border_bottom

        # Normalize texts to be a list of rows, where each row is a list of columns
        normalized_texts = []
        for row in texts:
            if isinstance(row, list):
                normalized_texts.append(row)
            else:
                normalized_texts.append([row])

        num_rows = len(normalized_texts)

        # Normalize text_styles to be a list of lists matching normalized_texts
        if not text_styles:
            text_styles = [['default'] * len(row) for row in normalized_texts]
        elif isinstance(text_styles, str):
            # Apply same style to all texts
            text_styles = [[text_styles] * len(row) for row in normalized_texts]
        else:
            # Expand text_styles to match normalized_texts
            expanded_text_styles = []
            text_styles_len = len(text_styles)
            for idx, row in enumerate(normalized_texts):

                if idx < text_styles_len:
                    row_styles = text_styles[idx]
                    if isinstance(row_styles, str):
                        # Apply same style to all columns in this row
                        expanded_text_styles.append([row_styles] * len(row))
                    else:
                        expanded_text_styles.append(row_styles)
                else:
                    expanded_text_styles.append(['default'] * len(row))
            text_styles = expanded_text_styles

        # Similarly normalize alignments
        if not alignments:
            alignments = [['center'] * len(row) for row in normalized_texts]
        elif isinstance(alignments, str):
            # Apply same alignment to all texts
            alignments = [[alignments] * len(row) for row in normalized_texts]
        else:
            # Expand alignments to match normalized_texts
            expanded_alignments = []
            alignments_len = len(alignments)
            for idx, row in enumerate(normalized_texts):

                if idx < alignments_len:
                    row_alignments = alignments[idx]
                    if isinstance(row_alignments, str):
                        # Apply same alignment to all columns in this row
                        expanded_alignments.append([row_alignments] * len(row))
                    else:
                        expanded_alignments.append(row_alignments)
                else:
                    expanded_alignments.append(['center'] * len(row))
            alignments = expanded_alignments

        # Print top border if any
        if border_top:
            print(horiz_border_top)
            if blank_top_line:
                num_inner_borders = max(len(row) - 1 for row in normalized_texts if row)
                available_width = self.get_available_width(num_inner_borders=num_inner_borders)
                blank_text = ' '.center(available_width)
                left_border = vert_border_left if vert_border_left else ''
                right_border = vert_border_right if vert_border_right else ''
                print(f'{left_border}{blank_text}{right_border}')

        # Iterate over rows
        for row_idx, (row_texts, row_styles, row_aligns) in enumerate(zip(normalized_texts, text_styles, alignments)):
            if not row_texts:  # Check if the row is an empty list
                # Print the horizontal inner border
                print(horiz_border_inner)
                continue  # Skip to the next iteration

            num_columns = len(row_texts)
            num_inner_borders = num_columns - 1 if num_columns > 1 else 0

            # Compute total available width for the text
            available_width = self.get_available_width(num_inner_borders)

            # Allocate widths to columns
            section_width = available_width // num_columns
            leftover_space = available_width - (section_width * num_columns)

            column_widths = [section_width] * num_columns
            # Distribute leftover_space to the last columns
            for i in range(leftover_space):
                column_widths[-(i + 1)] += 1

            # For each column, align the text within its allocated width
            aligned_columns = []
            for col_idx, (text, style, align) in enumerate(zip(row_texts, row_styles, row_aligns)):
                aligned_text = self.align_text(text, align=align, available_width=column_widths[col_idx])
                styled_text = self.pc.apply_style(style, aligned_text)
                aligned_columns.append(styled_text)

            # Construct the line with borders and inner borders
            left_border = vert_border_left if vert_border_left else ''
            right_border = vert_border_right if vert_border_right else ''
            inner_border = vert_border_inner if vert_border_inner else ''
            line = left_border + inner_border.join(aligned_columns) + right_border

            print(line)

        # Print bottom border if any
        if border_bottom:
            if blank_bottom_line:
                num_inner_borders = max(len(row) - 1 for row in normalized_texts if row)
                available_width = self.get_available_width(num_inner_borders=num_inner_borders)
                blank_text = ' '.center(available_width)
                left_border = vert_border_left if vert_border_left else ''
                right_border = vert_border_right if vert_border_right else ''
                print(f'{left_border}{blank_text}{right_border}')
            print(horiz_border_bottom)



    def print_border_boxed_text(self, text, text_style=None, text_align='center',
                                subtext='', subtext_style=None, subtext_align='center',
                                all_borders_style=None,
                                horiz_border_top=True, horiz_border_top_style=None,
                                horiz_border_bottom=True, horiz_border_bottom_style=None,
                                text_vert_border_l_style=None, text_vert_border_r_style=None,
                                subtext_vert_border_l_style=None, subtext_vert_border_r_style=None,
                                first_line_blank=False):

        if not text_style:
            text_style = 'default'
        if not subtext_style:
            subtext_style = 'default'

        # Use all_borders_style as a fallback for individual border styles
        horiz_border_top_style = all_borders_style if all_borders_style and not horiz_border_top_style else horiz_border_top_style
        horiz_border_bottom_style = all_borders_style if all_borders_style and not horiz_border_bottom_style else horiz_border_bottom_style
        text_vert_border_l_style = all_borders_style if all_borders_style and not text_vert_border_l_style else text_vert_border_l_style
        text_vert_border_r_style = all_borders_style if all_borders_style and not text_vert_border_r_style else text_vert_border_r_style
        subtext_vert_border_l_style = all_borders_style if all_borders_style and not subtext_vert_border_l_style else subtext_vert_border_l_style
        subtext_vert_border_r_style = all_borders_style if all_borders_style and not subtext_vert_border_r_style else subtext_vert_border_r_style

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
                                 border_top=None, border_bottom=None,
                                 border_left=None, border_right=None,
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

        if border_top:
            print(border_top)

        for lines, text_style, text_align in zip(lines_list, text_styles, alignments):
            for line in lines:
                if line == 'invisible_text' or line == '':
                    line = ' '
                    aligned_text = self.align_text(line, available_width, text_align)
                else:
                    aligned_text = self.pc.apply_style(text_style, self.align_text(line, available_width, text_align))

                final_text = self.construct_text(border_left, border_right, aligned_text)

                print(final_text)

        if border_bottom:
            print(border_bottom)


    def print_border_boxed_text4(self, texts, text_styles=None, text_alignments=None,
                                 border_top=None, border_bottom=None,
                                 border_left=None, border_right=None,
                                 default_text_alignment='center',
                                 blank_top_line=True, blank_bottom_line=True,
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

        if border_top:
            print(border_top * horiz_border_height)
            if blank_top_line:
                blank_text = ' '.center(available_width)
                print(f'{border_left}{blank_text}{border_right}')

        for lines, text_style, text_align in zip(lines_list, text_styles, text_alignments):
            for line in lines:
                if line == 'invisible_text' or line == '' or line == ' ':
                    line = ' '
                    aligned_text = self.align_text(line, available_width, text_align)
                else:
                    aligned_text = self.pc.apply_style(text_style, self.align_text(line, available_width, text_align))

                final_text = self.construct_text(border_left, border_right, aligned_text)

                print(final_text)

        if border_bottom:
            if blank_bottom_line:
                blank_text = ' '.center(available_width)
                print(f'{border_left}{blank_text}{border_right}')
            print(border_bottom * horiz_border_height)



        if table_strs:
            if table_strs_horiz_border_top and isinstance(table_strs_horiz_border_top, bool):
                table_strs_horiz_border_top = border_top
            if table_strs_horiz_border_bottom and isinstance(table_strs_horiz_border_bottom, bool):
                table_strs_horiz_border_bottom = border_bottom
            if table_strs_vert_border_left and isinstance(table_strs_vert_border_left, bool):
                table_strs_vert_border_left = border_left
            if table_strs_vert_border_right and isinstance(table_strs_vert_border_right, bool):
                table_strs_vert_border_right = border_right


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

            if border_bottom:
                if blank_bottom_line:
                    blank_text = ' '.center(available_width)
                    print(f'{border_left}{blank_text}{border_right}')
                print(border_bottom)




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


    def print_multi_column_box_unified(self,
                                       columns,
                                       col_widths,
                                       col_styles=None,
                                       col_alignments=None,
                                       horiz_border_top=True,
                                       horiz_border_bottom=True,
                                       vert_border_left=True,
                                       vert_border_right=True,
                                       col_sep=None,
                                       col_sep_width=1,
                                       col_widths_percent=False):
        """
        Unified method that can replicate the behaviors of all four previous methods.

        - columns: list of column texts
        - col_widths: list of widths or percentages (if col_widths_percent=True). May contain one '' to auto-fill.
        - col_styles: list of styles corresponding to each column, or None
        - col_alignments: list of alignments ('left', 'right', 'center'), or None
        - horiz_border_top, horiz_border_bottom: control horizontal border printing
        - vert_border_left, vert_border_right: control vertical border printing
        - col_sep: string used as a column separator (if None, fallback to a simple space or vert_border)
        - col_sep_width: integer multiplier for repeating col_sep (like Method 4)
        - col_widths_percent: if True, treat numeric col_widths as percentages of available width.

        This single method can simulate all original methods by toggling parameters.
        """

        # Validate inputs
        if len(columns) != len(col_widths):
            raise ValueError("Number of columns and column widths must match.")

        if col_styles and len(col_styles) != len(columns):
            raise ValueError("Number of column styles must match number of columns.")

        if col_alignments and len(col_alignments) != len(columns):
            raise ValueError("Number of column alignments must match number of columns.")

        available_width = self.get_available_width()

        # Handle column percentages if requested
        if col_widths_percent or '' in col_widths:
            # Convert percentages to absolute integers
            converted_widths = []
            for w in col_widths:
                if w == '':
                    converted_widths.append('')
                else:
                    converted_widths.append(int(available_width * (w / 100)))
            col_widths = converted_widths

        # Determine total padding. For simplicity, assume padding similar to methods 2-4.
        # We have a vertical padding attribute; total padding depends on number of columns and separators.
        num_columns = len(columns)
        sig_columns = num_columns - 1

        # If no col_sep given, behave like Method 1: just a space or a vertical border
        if col_sep is None:
            # Default to a single space if no dedicated vertical char is set
            col_sep = ''
        col_sep = col_sep * col_sep_width

        # Estimate total padding. Each column might be padded with self.vert_padding.
        # For simplicity, assume the pattern used previously: each separator plus padding contributes space.
        # We'll do a rough calculation akin to methods 2-4:
        total_padding = (sig_columns * len(col_sep) * (len(self.vert_padding) * 2))

        # If there's a column with '' width, auto-fill it:
        if '' in col_widths:
            unspecified_index = col_widths.index('')
            specified_width = sum(w for w in col_widths if w != '' and isinstance(w, int))
            remaining_width = available_width - specified_width - total_padding
            if remaining_width < 0:
                raise ValueError("Not enough space to fill unspecified column width.")
            col_widths[unspecified_index] = remaining_width

        total_col_width = sum(col_widths)
        if total_col_width > available_width:
            raise ValueError("Total width of columns exceeds available width.")

        horiz_border = self.pc.apply_style('horiz_border', self.horiz_border)
        vert_border = self.pc.apply_style('vert_border', self.vert_border) if self.vert_border else ''

        if horiz_border_top:
            print(horiz_border)

        # Split columns into lines
        col_lines = [self.split_text_to_lines(col, col_widths[i]) for i, col in enumerate(columns)]
        max_lines = max(len(lines) for lines in col_lines)

        for line_num in range(max_lines):
            row = []
            for col_num in range(len(columns)):
                col_style = col_styles[col_num] if col_styles else 'default'
                col_align = col_alignments[col_num] if col_alignments else 'center'
                if line_num < len(col_lines[col_num]):
                    line = col_lines[col_num][line_num]
                    aligned_text = self.pc.apply_style(col_style,
                                                       self.align_text(line, col_widths[col_num], col_align),
                                                       fill_space=False)
                else:
                    aligned_text = self.pc.apply_style(col_style, ' ' * col_widths[col_num], fill_space=False)
                row.append(aligned_text)

            # Join with padding and col_sep
            row_text = f"{self.vert_padding}{col_sep}{self.vert_padding}".join(row)

            # Apply vertical borders if requested
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

    def print_multi_column_box_unified_B(self,
                                       columns,
                                       col_widths,
                                       col_styles=None,
                                       col_alignments=None,
                                       horiz_border_top=True,
                                       horiz_border_bottom=True,
                                       vert_border_left=True,
                                       vert_border_right=True,
                                       col_sep=None,
                                       col_widths_percent=False,
                                       col_sep_width=1):
        """
        Prints a multi-column box with configurable widths, styles, alignments, borders,
        and column separators. Combines functionality from multiple methods.

        Parameters:
            columns (list of str): Text for each column.
            col_widths (list of int or str): Widths for each column. If col_widths_percent is True,
                these should be percentages (numbers or empty string for unspecified).
                An empty string ('') indicates that the column width should be automatically
                calculated from the remaining space.
            col_styles (list of str, optional): Style names for each column.
            col_alignments (list of str, optional): Alignment specifiers for each column ('left',
                'center', 'right').
            horiz_border_top (bool): Whether to print the top horizontal border.
            horiz_border_bottom (bool): Whether to print the bottom horizontal border.
            vert_border_left (bool): Whether to print the left vertical border.
            vert_border_right (bool): Whether to print the right vertical border.
            col_sep (str, optional): Column separator string. Defaults to self.vert_char.
            col_widths_percent (bool): Interpret col_widths as percentages if True.
            col_sep_width (int): Multiplier for the column separator width.
        """
        # Validate input lengths
        num_columns = len(columns)
        if len(col_widths) != num_columns:
            raise ValueError("Number of columns and column widths must match.")
        if col_styles and len(col_styles) != num_columns:
            raise ValueError("Number of column styles must match number of columns.")
        if col_alignments and len(col_alignments) != num_columns:
            raise ValueError("Number of column alignments must match number of columns.")

        # Set defaults if not provided
        if col_sep is None:
            col_sep = self.vert_char
        effective_col_sep = col_sep * col_sep_width

        # Get available width from the environment
        available_width = self.get_available_width()

        # Determine extra padding. Here we assume each column gets left and right vertical padding.
        # For example, if self.vert_padding is " " (one space), then each column contributes 2 spaces.
        # Additionally, the effective separator appears between columns.
        left_right_padding = 2 * len(self.vert_padding) * num_columns
        sep_total = (num_columns - 1) * len(effective_col_sep)
        total_padding = left_right_padding + sep_total

        # If widths are percentages, convert them to absolute values
        if col_widths_percent:
            new_widths = []
            for w in col_widths:
                if w == '':
                    new_widths.append('')
                else:
                    # Convert percentage (w) to an absolute width from available_width minus total_padding.
                    new_widths.append(int((available_width - total_padding) * (w / 100)))
            col_widths = new_widths

        # Handle unspecified widths (marked as '')
        if '' in col_widths:
            # Sum widths that are specified (making sure to ignore any that are '')
            specified_width = sum(w for w in col_widths if w != '')
            remaining_width = available_width - total_padding - specified_width
            if remaining_width < 0:
                raise ValueError("Total width of specified columns plus padding exceeds available width.")
            # Distribute the remaining width to each unspecified column (if more than one, you might choose to divide equally)
            num_unspecified = col_widths.count('')
            auto_width = remaining_width // num_unspecified  # integer division; remainder can be handled if desired
            col_widths = [auto_width if w == '' else w for w in col_widths]

        # Verify that the total column widths (plus padding) do not exceed available width.
        if sum(col_widths) + total_padding > available_width:
            raise ValueError("Total width of columns (with padding) exceeds available width.")

        # Prepare borders (assuming self.horiz_border and self.vert_border are defined, and styling is applied via self.pc)
        styled_horiz_border = self.pc.apply_style('horiz_border', self.horiz_border) if self.horiz_border else ''
        styled_vert_border = self.pc.apply_style('vert_border', self.vert_border) if self.vert_border else ''

        # Print top horizontal border if requested
        if horiz_border_top and styled_horiz_border:
            print(styled_horiz_border)

        # Pre-split each column’s text into lines according to its width.
        col_lines = [self.split_text_to_lines(col, col_widths[i]) for i, col in enumerate(columns)]
        max_lines = max(len(lines) for lines in col_lines)

        # Print each row line by line
        for line_num in range(max_lines):
            row_parts = []
            for col_index in range(num_columns):
                style = col_styles[col_index] if col_styles else 'default'
                align = col_alignments[col_index] if col_alignments else 'center'
                # Retrieve the line if available, else use blank spaces.
                if line_num < len(col_lines[col_index]):
                    text_line = col_lines[col_index][line_num]
                else:
                    text_line = ' ' * col_widths[col_index]
                # Align the text within the column width.
                aligned_text = self.align_text(text_line, col_widths[col_index], align)
                # Apply the column’s style.
                styled_text = self.pc.apply_style(style, aligned_text, fill_space=False)
                # Add left and right vertical padding (assumed to be self.vert_padding)
                padded_text = f"{self.vert_padding}{styled_text}{self.vert_padding}"
                row_parts.append(padded_text)

            # Join the columns with the effective column separator.
            row_text = effective_col_sep.join(row_parts)

            # Optionally add vertical borders at the left and right.
            if vert_border_left:
                row_text = f"{styled_vert_border}{row_text}"
            if vert_border_right:
                row_text = f"{row_text}{styled_vert_border}"

            print(row_text)

        # Print bottom horizontal border if requested
        if horiz_border_bottom and styled_horiz_border:
            print(styled_horiz_border)

    def print_multi_column_box(self, columns, col_widths, col_styles=None, col_alignments=None,
                               double_space_content=False, double_space_content_top=False, double_space_content_bottom=False):

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


        horiz_border_top, vert_border_left, vert_border_inner, vert_border_right, horiz_border_bottom = self.build_styled_border_box(style='blue')

        if horiz_border_top:
            print(horiz_border_top)
            if (double_space_content or double_space_content_top) and (vert_border_left and vert_border_right):
                blank_line = ' '.center(available_width)
                print(f"{vert_border_left}{blank_line}{vert_border_right}")

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
                    aligned_text = self.pc.apply_style(col_style, ' ' * col_widths[col_num], fill_space=False)
                row.append(aligned_text)
            if vert_border_left and vert_border_right:
                print(f"{vert_border_left}{''.join(row)}{vert_border_right}")
            elif vert_border_left:
                print(f"{vert_border_left}{' '.join(row)}")
            elif vert_border_right:
                print(f"{' '.join(row)}{vert_border_right}")
            else:
                print(' '.join(row))

        if (double_space_content or double_space_content_bottom) and (vert_border_left and vert_border_right):
            blank_line = ' '.center(available_width)
            print(f"{vert_border_left}{blank_line}{vert_border_right}")

        if horiz_border_bottom:
            print(horiz_border_bottom)



    def print_multi_column_box2(self, columns, col_widths, col_styles=None, col_alignments=None,
                               horiz_border_top=True, horiz_border_bottom=True,
                               vert_border_left=True, vert_border_right=True, col_sep=None,
                                col_widths_percent=False, orig_behavior=False):

        if not col_sep:
            col_sep = self.vert_char

        if len(columns) != len(col_widths):
            raise ValueError("Number of columns and column widths must match.")

        if col_styles and len(col_styles) != len(columns):
            raise ValueError("Number of column styles must match number of columns.")

        if col_alignments and len(col_alignments) != len(columns):
            raise ValueError("Number of column alignments must match number of columns.")

        available_width = self.get_available_width()
        num_columns = len(columns)
        sig_columns = num_columns - 1
        #sep_length = len(self.vert_padding) * 3
        sep_length = len(self.vert_padding) * 2 + len(col_sep)
        total_padding = sig_columns * sep_length

        if col_widths_percent:
            # Convert percentages to absolute widths
            col_widths = [int(available_width * (w / 100)) if w != '' else '' for w in col_widths]


        if '' in col_widths:
            unspecified_index = col_widths.index('')
            if not orig_behavior:
                specified_width = sum(col_widths[i] for i in range(len(col_widths)) if i != unspecified_index and col_widths[i] != '')
            else:
                specified_width = sum(col_widths[i] for i in range(len(col_widths)) if i != unspecified_index)
            remaining_width = available_width - specified_width - total_padding
            col_widths[unspecified_index] = remaining_width

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


    def print_multi_column_box22(self, columns, col_widths, col_styles=None, col_alignments=None,
                            horiz_border_top=True, horiz_border_bottom=True,
                            vert_border_left=True, vert_border_right=True, col_sep=None,
                            col_widths_percent=False, orig_behavior=False):

        if not col_sep:
            col_sep = self.vert_char

        if len(columns) != len(col_widths):
            raise ValueError("Number of columns and column widths must match.")

        if col_styles and len(col_styles) != len(columns):
            raise ValueError("Number of column styles must match number of columns.")

        if col_alignments and len(col_alignments) != len(columns):
            raise ValueError("Number of column alignments must match number of columns.")

        available_width = self.get_available_width()
        num_columns = len(columns)
        sig_columns = num_columns - 1
        sep_length = len(self.inner_padding) * 2 + len(col_sep)
        total_padding = sig_columns * sep_length

        if col_widths_percent:
            # Convert percentages to absolute widths
            col_widths = [int(available_width * (w / 100)) if w != '' else '' for w in col_widths]

        if '' in col_widths:
            unspecified_index = col_widths.index('')
            if not orig_behavior:
                specified_width = sum(col_widths[i] for i in range(len(col_widths)) if i != unspecified_index and col_widths[i] != '')
            else:
                specified_width = sum(col_widths[i] for i in range(len(col_widths)) if i != unspecified_index)
            remaining_width = available_width - specified_width - total_padding
            col_widths[unspecified_index] = remaining_width

        total_col_width = sum(col_widths)
        if total_col_width > available_width:
            raise ValueError("Total width of columns exceeds available width.")


        border_top, border_left, border_inner, border_right, border_bottom = self.build_styled_border_box(horiz_style='horiz_border', vert_style='vert_border',
                                                                                                          border_inner=col_sep, border_inner_style='col_sep')

        if horiz_border_top:
            print(border_top)

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
                    aligned_text = self.pc.apply_style(col_style, self.align_text(line, col_widths[col_num], col_align), fill_space=False)
                else:
                    aligned_text = self.pc.apply_style(col_style, ' ' * col_widths[col_num], fill_space=False)
                row.append(aligned_text)
            row_text = border_inner.join(row)
            if vert_border_left and vert_border_right:
                print(f"{border_left}{row_text}{border_right}")
            elif vert_border_left:
                print(f"{border_left}{row_text}")
            elif vert_border_right:
                print(f"{row_text}{border_right}")
            else:
                print(f"{self.vert_padding}{row_text}{self.vert_padding}")

        if horiz_border_bottom:
            print(border_bottom)


    def print_multi_column_box2B(self, columns, col_widths, col_styles=None, horiz_col_alignments=None, vert_col_alignments=None,
                                 row_height=None,  # Optional: If None, dynamically adjusts to tallest column
                                 horiz_border_top=True, horiz_border_bottom=True,
                                 vert_border_left=True, vert_border_right=True, col_sep=None, col_sep_style='col_sep',
                                 col_widths_percent=False, orig_behavior=False):

        if not col_sep:
            col_sep = self.vert_char

        if len(columns) != len(col_widths):
            raise ValueError("Number of columns and column widths must match.")

        if col_styles and len(col_styles) != len(columns):
            raise ValueError("Number of column styles must match number of columns.")

        if horiz_col_alignments and len(horiz_col_alignments) != len(columns):
            raise ValueError("Number of column alignments must match number of columns.")

        # Validate vert_col_alignments if provided
        # It can be either a single string in ['top', 'center', 'bottom'] or a list with one entry per column.
        allowed_alignments = ['top', 'center', 'bottom']
        if vert_col_alignments:
            if isinstance(vert_col_alignments, str):
                if vert_col_alignments not in allowed_alignments:
                    raise ValueError("Invalid vertical alignment value. Use 'top', 'center', or 'bottom'.")
                # Convert single string to a list for all columns.
                vert_col_alignments = [vert_col_alignments] * len(columns)
            elif isinstance(vert_col_alignments, list):
                if len(vert_col_alignments) != len(columns):
                    raise ValueError("Number of vertical column alignments must match number of columns.")
                for alignment in vert_col_alignments:
                    if alignment not in allowed_alignments:
                        raise ValueError("Invalid vertical alignment value in list. Use 'top', 'center', or 'bottom'.")
            else:
                raise ValueError("vert_col_alignments must be either a string or a list.")

        else:
            # If no vertical alignment is provided, default to 'top' for all columns.
            vert_col_alignments = ['top'] * len(columns)

        available_width = self.get_available_width()
        num_columns = len(columns)
        sig_columns = num_columns - 1
        sep_length = len(self.vert_padding) * 2 + len(col_sep)
        #sep_length = len(self.vert_padding) * 3
        #total_padding = sig_columns * (len(self.vert_padding) * 3)
        total_padding = sig_columns * sep_length

        if col_widths_percent:
            # Convert percentages to absolute widths
            col_widths = [int(available_width * (w / 100)) if w != '' else '' for w in col_widths]

        if '' in col_widths:
            unspecified_index = col_widths.index('')
            if not orig_behavior:
                specified_width = sum(col_widths[i] for i in range(len(col_widths)) if i != unspecified_index and col_widths[i] != '')
            else:
                specified_width = sum(col_widths[i] for i in range(len(col_widths)) if i != unspecified_index)
            remaining_width = available_width - specified_width - total_padding
            col_widths[unspecified_index] = remaining_width

        total_col_width = sum(col_widths)
        if total_col_width > available_width:
            raise ValueError("Total width of columns exceeds available width.")

        horiz_border = self.pc.apply_style('horiz_border', self.horiz_border)
        vert_border = self.pc.apply_style('vert_border', self.vert_border) if self.vert_border else ''

        border_top, border_left, border_inner, border_right, border_bottom = self.build_styled_border_box(horiz_style='horiz_border', vert_style='vert_border', border_inner=col_sep, border_inner_style=col_sep_style)

        if horiz_border_top:
            print(border_top)


        # Generate multi-line column content dynamically
        formatted_columns = []
        max_lines = 0  # Track max number of lines across all columns

        for i, col in enumerate(columns):
            col_width = col_widths[i]
            col_lines = self.split_text_to_lines(col, col_width)
            formatted_columns.append(col_lines)
            max_lines = max(max_lines, len(col_lines))  # Determine tallest column

        # If row_height is specified, use it. Otherwise, use max_lines.
        row_height = row_height or max_lines




        # For each column, pad the content vertically according to the desired alignment.
        # If vert_col_alignments is provided, use it; otherwise, use 'center' if all_vertically_centered is True, else 'top'
        for i in range(len(formatted_columns)):
            col_lines = formatted_columns[i]
            extra_padding = row_height - len(col_lines)  # Compute missing lines
            if extra_padding > 0:
                align = vert_col_alignments[i]

                if align == 'top':
                    top_pad = 0
                    bottom_pad = extra_padding
                elif align == 'bottom':
                    top_pad = extra_padding
                    bottom_pad = 0
                elif align == 'center':
                    top_pad = extra_padding // 2
                    bottom_pad = extra_padding - top_pad
                else:
                    # Should never happen due to earlier validation.
                    top_pad = 0
                    bottom_pad = extra_padding

                formatted_columns[i] = (
                        [" " * col_widths[i]] * top_pad +
                        col_lines +
                        [" " * col_widths[i]] * bottom_pad
                )
            # If no extra padding is needed, leave the column as is.

        # Print each row of columns
        for line_num in range(row_height):
            row = []
            for col_num in range(len(columns)):
                col_style = col_styles[col_num] if col_styles else 'default'
                col_align = horiz_col_alignments[col_num] if horiz_col_alignments else 'center'


                line = formatted_columns[col_num][line_num] if line_num < len(formatted_columns[col_num]) else " " * col_widths[col_num]
                aligned_text = self.pc.apply_style(col_style, self.align_text(line, col_widths[col_num], col_align), fill_space=False)
                row.append(aligned_text)

            row_text = border_inner.join(row)

            if vert_border_left and vert_border_right:
                print(f"{border_left}{row_text}{border_right}")
            elif vert_border_left:
                print(f"{border_left}{' '.join(row)}")
            elif vert_border_right:
                print(f"{' '.join(row)}{border_right}")
            else:
                print(f"{' '.join(row)}")


        if horiz_border_bottom:
            print(border_bottom)




    def print_multi_column_box2C(self, columns, col_widths, col_styles=None, horiz_col_alignments=None, vert_col_alignments=None,
                                row_height=1,  # Defines total row height including text & padding
                                horiz_border_top=True, horiz_border_bottom=True,
                                vert_border_left=True, vert_border_right=True, col_sep=None, col_sep_style=None,
                                col_widths_percent=False, orig_behavior=False):

        if not col_sep:
            col_sep = self.vert_char

        if len(columns) != len(col_widths):
            raise ValueError("Number of columns and column widths must match.")

        if col_styles and len(col_styles) != len(columns):
            raise ValueError("Number of column styles must match number of columns.")

        if horiz_col_alignments and len(horiz_col_alignments) != len(columns):
            raise ValueError("Number of column alignments must match number of columns.")

        available_width = self.get_available_width()
        num_columns = len(columns)
        sig_columns = num_columns - 1
        #sep_length = len(self.vert_padding) * 3
        sep_length = len(self.vert_padding) * 2 + len(col_sep)
        total_padding = sig_columns * sep_length

        if col_widths_percent:
            # Convert percentages to absolute widths
            col_widths = [int(available_width * (w / 100)) if w != '' else '' for w in col_widths]

        if '' in col_widths:
            unspecified_index = col_widths.index('')
            if not orig_behavior:
                specified_width = sum(col_widths[i] for i in range(len(col_widths)) if i != unspecified_index and col_widths[i] != '')
            else:
                specified_width = sum(col_widths[i] for i in range(len(col_widths)) if i != unspecified_index)
            remaining_width = available_width - specified_width - total_padding
            col_widths[unspecified_index] = remaining_width

        total_col_width = sum(col_widths)
        if total_col_width > available_width:
            raise ValueError("Total width of columns exceeds available width.")

        horiz_border = self.pc.apply_style('purple', self.horiz_border)
        vert_border = self.pc.apply_style('orange', self.vert_border) if self.vert_border else ''

        if horiz_border_top:
            print(horiz_border)

        # Generate multi-line button content
        formatted_columns = []
        for i, col in enumerate(columns):
            col_width = col_widths[i]
            col_lines = self.split_text_to_lines(col, col_width)

            # Enforce button height with padding
            total_lines = len(col_lines)
            extra_padding = max(0, row_height - total_lines)  # Compute padding needed

            padding_top = extra_padding // 2
            padding_bottom = extra_padding - padding_top

            formatted_column = (
                    [" " * col_width] * padding_top +  # Top padding
                    col_lines +  # Actual content
                    [" " * col_width] * padding_bottom  # Bottom padding
            )
            formatted_columns.append(formatted_column)

        max_lines = row_height  # Force consistent row height

        # Print each row of buttons
        for line_num in range(max_lines):
            row = []
            for col_num in range(len(columns)):
                col_style = col_styles[col_num] if col_styles else 'default'
                col_align = horiz_col_alignments[col_num] if horiz_col_alignments else 'center'
                line = formatted_columns[col_num][line_num]  # Get correct line
                aligned_text = self.pc.apply_style(col_style, self.align_text(line, col_widths[col_num], col_align), fill_space=False)
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

        horiz_border = self.pc.apply_style('horiz_border', self.horiz_border)
        vert_border = self.pc.apply_style('vert_border', self.vert_border) if self.vert_border else ''

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

        horiz_border = self.pc.apply_style('horiz_border', self.horiz_border)
        vert_border = self.pc.apply_style('vert_border', self.vert_border) if self.vert_border else ''

        if horiz_border_top:
            print(horiz_border)

        col_lines = [self.split_text_to_lines(col, col_widths[i]) for i, col in enumerate(columns)]
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

    def print_unified_border_boxed_tables(self,
                                          table_strs,
                                          horiz_border_top=None,
                                          vert_border_left=None,
                                          vert_border_right=None,
                                          horiz_border_bottom=None,
                                          # Core parameters controlling behavior:
                                          single_table_mode=False,
                                          equal_width_distribution=False,
                                          dynamic_wrapping=False,
                                          # Alignment parameters:
                                          # If single_table_mode=True, use main_text_align for that one table.
                                          # If multiple tables, provide table_alignments as a list, one per table.
                                          main_text_align='center',
                                          table_alignments=None,
                                          # Spacing/padding:
                                          table_padding=4,
                                          # Style parameters (optional, could be applied if defined in your class):
                                          table_style=None,
                                          text_style=None):
        """
        A highly configurable method unifying functionalities of multiple original methods.
        By tweaking parameters, this method can emulate the behaviors of:
          - print_border_boxed_table      (Single table, uniform alignment)
          - print_border_boxed_tables     (Multiple tables, dynamic wrapping)
          - print_border_boxed_tables2    (Multiple tables, equal-width distribution, per-table alignment)
          - print_border_boxed_tables4    (Multiple tables, equal-width distribution, per-table alignment, custom padding)

        Parameters:
        -----------
        table_strs : str or list of str
            If single_table_mode=True, this can be a single string representing the table.
            Otherwise, pass a list of strings, each representing one table.

        horiz_border_top : str or None
            The top horizontal border line. If None, no top border is printed.

        vert_border_left : str or None
            The left vertical border character/string. If None, no left border is printed.

        vert_border_right : str or None
            The right vertical border character/string. If None, no right border is printed.

        horiz_border_bottom : str or None
            The bottom horizontal border line. If None, no bottom border is printed.

        single_table_mode : bool
            - True  => Behave like 'print_border_boxed_table':
                       Print a single table with borders and uniform text alignment (main_text_align).
            - False => Expect multiple tables (list of table strings) and print them side-by-side.

        equal_width_distribution : bool
            - When False:
                If printing multiple tables and dynamic_wrapping=True, this behaves like print_border_boxed_tables:
                It will dynamically wrap lines, trying not to exceed available width.
            - When True:
                Distribute the available width evenly among tables (like print_border_boxed_tables2 / print_border_boxed_tables4).
                Each table gets a fixed section width, and each line is aligned within its section.

        dynamic_wrapping : bool
            - True  => Similar to print_border_boxed_tables:
                       If multiple tables exceed available width in one line, it wraps them to the next line.
            - False => No dynamic wrapping. If equal_width_distribution=False and multiple tables are large,
                       they may not fit well. Usually you'd set equal_width_distribution=True if not wrapping.

        main_text_align : str
            - For single_table_mode, this sets alignment: 'left', 'center', or 'right'.
            - Ignored if multiple tables and table_alignments is provided.
            Default is 'center'.

        table_alignments : list of str or None
            - For multiple tables, a list specifying alignment for each table. e.g. ['left', 'center', 'right']
            - If None, defaults to 'left' for each table in multiple table mode.
            - If single_table_mode=True, this is ignored.

        table_padding : int
            The number of spaces between tables when multiple tables are printed side-by-side.
            - For single_table_mode, this is not very relevant since there's only one table.
            - For multiple tables without equal_width_distribution, it may or may not apply depending on wrapping logic.
            - For equal_width_distribution=True, behaves like print_border_boxed_tables4, controlling spacing between columns.

        table_style, text_style :
            These parameters are placeholders if you have styling logic. Not demonstrated fully here.

        How to Achieve Original Behaviors:
        ---------------------------------
        1. Behave like `print_border_boxed_table` (single table):
           - Set single_table_mode=True
           - Provide a single table_str (not a list)
           - Choose main_text_align (e.g. 'center') and provide borders
           Example:
             print_unified_border_boxed_tables(self,
                                               table_strs="Single Table Content",
                                               horiz_border_top="=====",
                                               vert_border_left="|",
                                               vert_border_right="|",
                                               horiz_border_bottom="=====",
                                               single_table_mode=True,
                                               main_text_align='center')

        2. Behave like `print_border_boxed_tables` (multiple tables, dynamic line wrapping):
           - single_table_mode=False
           - multiple table_strs in a list
           - dynamic_wrapping=True
           - equal_width_distribution=False
           Example:
             print_unified_border_boxed_tables(self,
                                               table_strs=[table1_str, table2_str, table3_str],
                                               horiz_border_top="=====",
                                               vert_border_left="|",
                                               vert_border_right="|",
                                               horiz_border_bottom="=====",
                                               single_table_mode=False,
                                               dynamic_wrapping=True,
                                               equal_width_distribution=False,
                                               table_padding=4)

        3. Behave like `print_border_boxed_tables2` (multiple tables, equal widths, per-table align):
           - single_table_mode=False
           - equal_width_distribution=True
           - dynamic_wrapping=False
           - table_alignments=['left','center','right'] etc.
           Example:
             print_unified_border_boxed_tables(self,
                                               table_strs=[table1_str, table2_str],
                                               horiz_border_top="=====",
                                               vert_border_left="|",
                                               vert_border_right="|",
                                               horiz_border_bottom="=====",
                                               single_table_mode=False,
                                               equal_width_distribution=True,
                                               table_alignments=['left', 'center'])

        4. Behave like `print_border_boxed_tables4` (multiple tables, equal widths, padding):
           - single_table_mode=False
           - equal_width_distribution=True
           - table_alignments=['left', 'center', ...]
           - table_padding=4 (or another number)
           - dynamic_wrapping=False
           Example:
             print_unified_border_boxed_tables(self,
                                               table_strs=[table1_str, table2_str],
                                               horiz_border_top="=====",
                                               vert_border_left="|",
                                               vert_border_right="|",
                                               horiz_border_bottom="=====",
                                               single_table_mode=False,
                                               equal_width_distribution=True,
                                               table_alignments=['center','right'],
                                               table_padding=4)

        This method attempts to unify all functionalities.
        Adjust parameters accordingly.
        """

        # -----------------------------------------------------
        # Obtain and preprocess input
        # -----------------------------------------------------
        available_width = self.get_available_width()
        if single_table_mode and isinstance(table_strs, str):
            # Convert single string to a list of one element for uniform processing
            table_strs = [table_strs]
        elif not isinstance(table_strs, list):
            raise ValueError("table_strs must be a list when not in single_table_mode, or a string/list if single_table_mode.")

        # Split each table into lines
        table_lines_list = [table_str.split("\n") for table_str in table_strs]
        max_lines = max(len(table_lines) for table_lines in table_lines_list)

        # Normalize line counts per table so they are all the same height
        for table_lines in table_lines_list:
            table_lines += [''] * (max_lines - len(table_lines))

        # Determine alignment strategy
        if single_table_mode:
            # In single table mode, we only have one table and one alignment (main_text_align)
            alignments = [main_text_align]
        else:
            # Multiple tables
            if table_alignments is None:
                # Default to left align if not specified
                alignments = ['left'] * len(table_strs)
            else:
                # Use provided alignments; if fewer alignments than tables, default the rest to left
                alignments = list(table_alignments) + ['left'] * (len(table_strs) - len(table_alignments))

        # -----------------------------------------------------
        # Print top border if provided
        # -----------------------------------------------------
        if horiz_border_top:
            print(horiz_border_top)

        # Print a blank line under top border if vertical borders are given
        # (Mimicking original behavior)
        blank_line = None
        if vert_border_left and vert_border_right:
            blank_line = ' '.center(available_width)
            print(f"{vert_border_left}{blank_line}{vert_border_right}")

        # -----------------------------------------------------
        # If single_table_mode: just center/align the lines and print
        # -----------------------------------------------------
        if single_table_mode:
            # Single table mode similar to print_border_boxed_table
            for line in table_lines_list[0]:
                stripped_line = self.strip_ansi_escape_sequences(line)
                padding_needed = available_width - len(stripped_line)
                current_align = alignments[0]  # main_text_align
                if current_align == 'center':
                    leading_spaces = padding_needed // 2
                    trailing_spaces = padding_needed - leading_spaces
                    aligned_line = ' ' * leading_spaces + line + ' ' * trailing_spaces
                elif current_align == 'left':
                    aligned_line = line + ' ' * padding_needed
                else:  # right align
                    aligned_line = ' ' * padding_needed + line

                # Construct final line with borders if they exist
                left_border = vert_border_left if vert_border_left else ''
                right_border = vert_border_right if vert_border_right else ''
                print(f"{left_border}{aligned_line}{right_border}")

            # Print bottom border if provided
            if horiz_border_bottom:
                # Print a blank line above bottom if borders present (mimicking original)
                if vert_border_left and vert_border_right and not blank_line:
                    blank_line = ' '.center(available_width)
                    print(f"{vert_border_left}{blank_line}{vert_border_right}")
                print(horiz_border_bottom)

            return  # End single table mode here

        # -----------------------------------------------------
        # Multiple tables mode
        # -----------------------------------------------------

        if equal_width_distribution:
            # -----------------------------------------------------
            # equal_width_distribution=True
            # This is like print_border_boxed_tables2 or print_border_boxed_tables4
            # We will distribute the width evenly among tables.
            # -----------------------------------------------------
            num_tables = len(table_strs)

            # Compute how much width each table gets:
            # If dynamic_wrapping is True here, it doesn't really apply
            # because equal_width_distribution suggests a fixed layout.
            # We'll ignore dynamic_wrapping in this scenario.
            total_padding_space = (num_tables - 1) * table_padding
            section_width = (available_width - total_padding_space) // num_tables

            # Print each line:
            for line_index in range(max_lines):
                row_parts = []
                for table_index, table_lines in enumerate(table_lines_list):
                    line = table_lines[line_index]
                    stripped_line = self.strip_ansi_escape_sequences(line)
                    current_align = alignments[table_index]

                    # Align text within section_width
                    aligned_line = self.align_text(line, section_width, current_align)
                    row_parts.append(aligned_line)

                # Join parts with table_padding spaces
                row = (' ' * table_padding).join(row_parts)

                # Ensure we do not exceed available width. If it does, it will just truncate visually.
                stripped_row = self.strip_ansi_escape_sequences(row)
                row_length = len(stripped_row)
                padding_needed = max(0, available_width - row_length)

                left_border = vert_border_left if vert_border_left else ''
                right_border = vert_border_right if vert_border_right else ''
                print(f"{left_border}{row + ' ' * padding_needed}{right_border}")

            # Print bottom border if provided
            if horiz_border_bottom:
                # If we have vertical borders, print a blank line above bottom border (mimicking original)
                if vert_border_left and vert_border_right and not blank_line:
                    blank_line = ' '.center(available_width)
                    print(f"{vert_border_left}{blank_line}{vert_border_right}")
                print(horiz_border_bottom)

        else:
            # -----------------------------------------------------
            # equal_width_distribution=False
            # Potentially dynamic wrapping mode like print_border_boxed_tables
            # or just print them inline without equal width if dynamic_wrapping=False.
            #
            # If dynamic_wrapping=True: emulate print_border_boxed_tables
            #   - We try to place tables side by side until exceeding width, then wrap.
            # If dynamic_wrapping=False:
            #   - We just place them one after the other in a single row, might overflow.
            # -----------------------------------------------------
            if dynamic_wrapping:
                # Like print_border_boxed_tables
                # We'll try to place tables line by line, wrapping when necessary.
                row_buffer = []
                # We build rows by iterating over each line index and each table in turn
                for line_index in range(max_lines):
                    current_width = 0
                    row = ""
                    for table_index, table_lines in enumerate(table_lines_list):
                        line = table_lines[line_index]
                        stripped_line = self.strip_ansi_escape_sequences(line)
                        line_length = len(stripped_line)

                        # Check if adding this table line plus padding would exceed width
                        extra_space = table_padding if row else 0  # Add padding if not the first in row
                        if current_width + extra_space + line_length > available_width:
                            # Push the current row and start a new one
                            row_buffer.append(row.rstrip())
                            row = ""
                            current_width = 0

                        # Add table line to current row
                        if row:
                            row += " " * table_padding
                            current_width += table_padding
                        row += line
                        current_width += line_length

                    if row:
                        row_buffer.append(row.rstrip())

                # Now we have row_buffer with each row. Let's center them.
                # In the original print_border_boxed_tables, final alignment was center.
                for row in row_buffer:
                    stripped_row = self.strip_ansi_escape_sequences(row)
                    row_length = len(stripped_row)
                    # Center align the entire row
                    leading_spaces = (available_width - row_length) // 2
                    if (available_width - row_length) % 2 != 0:
                        leading_spaces += 1
                    aligned_text = ' ' * leading_spaces + row
                    # Add borders
                    padding_needed = available_width - len(self.strip_ansi_escape_sequences(aligned_text))
                    left_border = vert_border_left if vert_border_left else ''
                    right_border = vert_border_right if vert_border_right else ''
                    print(f"{left_border}{aligned_text + ' ' * padding_needed}{right_border}")

                # Bottom border if provided
                if horiz_border_bottom:
                    if vert_border_left and vert_border_right:
                        if not blank_line:
                            blank_line = ' '.center(available_width)
                        print(f"{vert_border_left}{blank_line}{vert_border_right}")
                    print(horiz_border_bottom)

            else:
                # equal_width_distribution=False, dynamic_wrapping=False
                # This scenario is less clearly defined in the original code, but we can:
                # - Print all tables side by side on each line without wrapping.
                # - Align each table line according to alignments, but since no equal width,
                #   we just align them as if each table occupies only its content width.
                # - We'll just place them separated by table_padding spaces.
                #
                # Note: Without equal width or wrapping, "alignment" is ambiguous. We'll align each line
                # within its own natural width only. In other words, 'center' or 'right' won't do much
                # since there's no section width.
                # We'll interpret alignment as follows:
                # - left: leave line as is
                # - center or right: we'll try to align it within the length of the longest line of that table column
                #   This requires finding max width per "table column". Let's do that.

                num_tables = len(table_strs)
                # Compute max line length per table to better handle center/right align
                max_widths = []
                for t_lines in table_lines_list:
                    max_widths.append(max(len(self.strip_ansi_escape_sequences(l)) for l in t_lines))

                for line_index in range(max_lines):
                    row_parts = []
                    for table_index, table_lines in enumerate(table_lines_list):
                        line = table_lines[line_index]
                        stripped_line = self.strip_ansi_escape_sequences(line)
                        current_align = alignments[table_index]
                        col_width = max_widths[table_index]
                        padding_needed = col_width - len(stripped_line)

                        if current_align == 'center':
                            leading_spaces = padding_needed // 2
                            trailing_spaces = padding_needed - leading_spaces
                            aligned_line = ' ' * leading_spaces + line + ' ' * trailing_spaces
                        elif current_align == 'right':
                            aligned_line = ' ' * padding_needed + line
                        else:  # left
                            aligned_line = line + ' ' * padding_needed

                        row_parts.append(aligned_line)

                    # Join with table_padding spaces
                    row = (' ' * table_padding).join(row_parts)
                    # Add borders and print
                    stripped_row = self.strip_ansi_escape_sequences(row)
                    row_length = len(stripped_row)
                    padding_needed = max(0, available_width - row_length)
                    left_border = vert_border_left if vert_border_left else ''
                    right_border = vert_border_right if vert_border_right else ''
                    print(f"{left_border}{row + ' ' * padding_needed}{right_border}")

                # Bottom border if provided
                if horiz_border_bottom:
                    if vert_border_left and vert_border_right and not blank_line:
                        blank_line = ' '.center(available_width)
                        print(f"{vert_border_left}{blank_line}{vert_border_right}")
                    print(horiz_border_bottom)