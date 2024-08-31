from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from prints_charming import (
    PrintsCharming,
    DEFAULT_CONFIG,
    DEFAULT_COLOR_MAP,
    DEFAULT_EFFECT_MAP,
    DEFAULT_STYLES,
    DEFAULT_LOGGING_STYLES
)



class TableManager:
    def __init__(self, pc: PrintsCharming = None, style_themes: dict = None, conditional_styles: dict = None):
        self.pc = pc or PrintsCharming(color_map=DEFAULT_COLOR_MAP.copy(), styles=DEFAULT_STYLES.copy())
        self.style_themes = style_themes
        self.conditional_styles = conditional_styles
        self.tables = {}

        self.border_char = "-"
        self.col_sep = " | "
        self.title_style = "header_text"


    def generate_table(self,
                       table_data: List[List[Any]],
                       table_name: str = None,
                       show_table_name: bool = False,
                       table_style: str = "default",
                       border_char: str = "-",
                       col_sep: str = " | ",
                       border_style: Optional[str] = None,
                       col_sep_style: Optional[str] = None,
                       header_style: Optional[str] = None,
                       header_column_styles: Optional[Dict[int, str]] = None,
                       col_alignments: Optional[List[str]] = None,
                       default_column_styles: Optional[Dict[int, str]] = None,
                       cell_style: Optional[str or list] = None,
                       target_text_box: bool = False,
                       conditional_style_functions: Optional[Dict[str, Callable[[Any], Optional[str]]]] = None,
                       double_space: bool = False,
                       use_styles=True
                       ) -> str:

        """
        Generates a table with optional styling and alignment as a string.

        :param table_data: A list of lists representing the rows of the table.
        :param col_alignments: A list of strings ('left', 'center', 'right') for column alignments.
        :param cell_style: Style name for the table cells.
        :param header_style: Style name for the header row.
        :param header_column_styles: A dictionary mapping column indices to style names for the header row.
        :param border_style: Style name for the table borders.
        :param column_styles: A dictionary mapping column indices to style names.
        :param conditional_styles: A dictionary defining conditional styles based on cell values.
        :return: A string representing the formatted table.
        """

        if use_styles:
            styled_col_sep = self.pc.apply_style(col_sep_style, col_sep) if col_sep_style else col_sep
        else:
            styled_col_sep = self.pc.apply_color(col_sep_style, col_sep) if col_sep_style else col_sep

        # 1. Automatic Column Sizing
        max_col_lengths = [0] * len(table_data[0])
        for row in table_data:
            for i, cell in enumerate(row):
                cell_length = len(str(cell))
                max_col_lengths[i] = max(max_col_lengths[i], cell_length)

        # 2. Column Alignment
        table_output = []
        header = table_data[0]

        for row_idx, row in enumerate(table_data):
            aligned_row = []
            for i, cell in enumerate(row):
                cell_str = str(cell)
                max_length = max_col_lengths[i]

                # Determine the alignment for this cell
                alignment = 'left'  # Default
                if col_alignments and i < len(col_alignments):
                    alignment = col_alignments[i]
                elif isinstance(cell, (int, float)):
                    alignment = 'right'

                # Apply the alignment
                if alignment == 'left':
                    aligned_cell = cell_str.ljust(max_length)
                elif alignment == 'center':
                    aligned_cell = cell_str.center(max_length)
                elif alignment == 'right':
                    aligned_cell = cell_str.rjust(max_length)
                else:
                    aligned_cell = cell_str.ljust(max_length)  # Fallback

                # Apply the style
                if row_idx == 0:
                    # Apply header styles
                    if header_column_styles and i in header_column_styles:
                        aligned_cell = self.pc.apply_style(header_column_styles[i], aligned_cell)
                    elif header_style:
                        aligned_cell = self.pc.apply_style(header_style, aligned_cell)
                else:
                    if header[i] == 'Color Name':
                        aligned_cell = self.pc.apply_color(cell_str, aligned_cell)
                    elif header[i] == 'Foreground Text':
                        color_name = row[0]  # Assuming the first column is the color name
                        aligned_cell = self.pc.apply_color(color_name, aligned_cell)
                    elif header[i] == 'Background Block':
                        color_name = row[0]  # Assuming the first column is the color name
                        aligned_cell = self.pc.return_bg(color_name, length=max_length)
                    elif header[i] == 'Style Name':
                        aligned_cell = self.pc.apply_style(cell_str, aligned_cell)
                    elif header[i] == 'Styled Text':
                        style_name = row[0]
                        aligned_cell = self.pc.apply_style(style_name, aligned_cell)
                    elif header[i] == 'Style Definition':
                        aligned_cell = self.pc.apply_style('default', aligned_cell)

                    # Apply conditional styles if provided
                    elif conditional_style_functions and header[i] in conditional_style_functions:
                        # Check if the function requires the entire row as an argument
                        if conditional_style_functions[header[i]].__code__.co_argcount == 2:
                            style = conditional_style_functions[header[i]](cell, row)
                        else:
                            style = conditional_style_functions[header[i]](cell)
                        if style:
                            aligned_cell = self.pc.apply_style(style, aligned_cell)
                        else:
                            if default_column_styles and i in default_column_styles:
                                # Apply column-specific styles if provided
                                aligned_cell = self.pc.apply_style(default_column_styles[i], aligned_cell)
                    elif default_column_styles and i in default_column_styles:
                        # Apply column-specific styles if provided
                        aligned_cell = self.pc.apply_style(default_column_styles[i], aligned_cell)
                    elif cell_style:
                        if isinstance(cell_style, list):
                            # Apply alternating styles based on the row index
                            style_to_apply = cell_style[0] if row_idx % 2 == 1 else cell_style[1]
                            aligned_cell = self.pc.apply_style(style_to_apply, aligned_cell)
                        else:
                            aligned_cell = self.pc.apply_style(cell_style, aligned_cell)


                # Add aligned and styled cell to the row
                aligned_row.append(aligned_cell)

            # Create a row string and add to table output
            if target_text_box:
                row_str = self.pc.apply_style(col_sep_style, col_sep.lstrip()) + styled_col_sep.join(aligned_row) + self.pc.apply_style(col_sep_style, col_sep.rstrip())
            else:
                row_str = styled_col_sep + styled_col_sep.join(aligned_row) + styled_col_sep
            table_output.append(row_str)

        # 3. Generate Borders and Rows
        table_str = ""
        border_line = ""  # Initialize border_line to ensure it always has a value
        if border_style:
            border_length = sum(max_col_lengths) + len(max_col_lengths) * len(col_sep) + len(col_sep) - 2
            border_line = self.pc.apply_style(border_style, border_char * border_length)
            #print(f' {border_line}')
            if target_text_box:
                table_str += f'{border_line}\n'
            else:
                table_str += f' {border_line}\n'

        if show_table_name and table_name:
            centered_table_name = self.pc.apply_style(self.title_style, table_name.center(border_length))
            table_str += f'{centered_table_name}\n'
            if border_style:
                table_str += f'{border_line}\n'

        for i, row in enumerate(table_output):
            #print(row)
            table_str += row + "\n"
            if i != 0 and double_space:
                table_str += "\n"
            #if double_space:
                #table_str += "\n"
            if i == 0 and (header_style or header_column_styles) and border_style:
                #print(f' {border_line}')
                if target_text_box:
                    table_str += f'{border_line}\n'
                else:
                    table_str += f' {border_line}\n'

        if border_style:
            #print(f' {border_line}')
            if target_text_box:
                table_str += f'{border_line}\n'
            else:
                table_str += f' {border_line}\n'

        return table_str


