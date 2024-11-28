# table_manager.py

import os
import time
import random
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
import copy
import re


ANSI_ESCAPE = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')



class BoundCell:
    def __init__(self, data_source: Callable[[], Any]):
        self.data_source = data_source

    def get_value(self) -> Any:
        return self.data_source()




class TableManager:
    _shared_instances = {}

    @classmethod
    def get_shared_instance(cls, key):
        """
        Get a shared TableManager instance.

        Returns:
            TableManager: A shared TableManager instance or None if not set.
        """
        return cls._shared_instances.get(key)

    @classmethod
    def set_shared_instance(cls, key, instance):
        """
        Set a shared TableManager instance.

        Args:
            key (str): The dictionary key used to identify the instance.
            instance (TableManager): The TableManager instance to set as shared.
        """
        cls._shared_instances[key] = instance


    def __init__(self, pc: Union[PrintsCharming, str, None] = None, style_themes: dict = None, conditional_styles: dict = None, specific_headers: dict = None):
        if isinstance(pc, str):
            self.pc = PrintsCharming.get_shared_instance(pc)
            if not self.pc:
                self.pc = PrintsCharming()
                self.pc.warning(f"No shared instance found for key '{pc}'. Using a new instance with default init.")
        else:
            self.pc = pc or PrintsCharming()

        self.style_themes = style_themes
        self.conditional_styles = conditional_styles
        self.specific_headers = specific_headers or {}
        self.tables = {}
        self.previous_values = {}

        self.border_char = "-"
        self.col_sep = " | "
        self.title_style = "header_text"

        self.debug = self.pc.debug




    def add_specific_headers(self, name: str, specific_headers: Dict[str, Callable[[Any, List[Any], int, int, int], str]]):
        """
        Adds or updates a specific_headers configuration with the given name.

        Args:
            name (str): The name to assign to the specific_headers configuration.
            specific_headers (dict): A dictionary of header-specific formatting functions.
        """
        if not isinstance(specific_headers, dict):
            raise ValueError("specific_headers must be a dictionary of column-specific formatting functions.")

        self.specific_headers[name] = specific_headers




    def format_cell(self, cell, row, row_idx, col_idx, max_col_lengths, header, format_params):
        cell_str = str(cell)
        max_length = max_col_lengths[col_idx]

        # Determine alignment
        alignment = 'left'  # Default alignment
        col_alignments = format_params.get('col_alignments')
        if col_alignments and col_idx < len(col_alignments):
            alignment = col_alignments[col_idx]
        elif isinstance(cell, (int, float)):
            alignment = 'right'

        # Apply alignment
        if alignment == 'left':
            aligned_cell = cell_str.ljust(max_length)
        elif alignment == 'center':
            aligned_cell = cell_str.center(max_length)
        elif alignment == 'right':
            aligned_cell = cell_str.rjust(max_length)
        else:
            aligned_cell = cell_str.ljust(max_length)  # Fallback

        # Apply styles
        use_styles = format_params.get('use_styles', True)
        if row_idx == 0:
            # Header row styles
            header_style = format_params.get('header_style')
            header_column_styles = format_params.get('header_column_styles')
            if header_column_styles and col_idx in header_column_styles:
                aligned_cell = self.pc.apply_style(header_column_styles[col_idx], aligned_cell)
            elif header_style:
                aligned_cell = self.pc.apply_style(header_style, aligned_cell)
        else:
            # Data row styles
            conditional_style_functions = format_params.get('conditional_style_functions')
            default_column_styles = format_params.get('default_column_styles')
            specific_headers = format_params.get('specific_headers', {})
            cell_style = format_params.get('cell_style')
            column_name = header[col_idx]

            # Handle specific headers
            if specific_headers and column_name in specific_headers:
                specific_handler = specific_headers[column_name]
                aligned_cell = specific_handler(cell_str, aligned_cell, row, row_idx, col_idx, max_length)

            # Apply conditional styles if provided
            elif conditional_style_functions and column_name in conditional_style_functions:
                style_func = conditional_style_functions[column_name]
                # Check if the function requires the entire row as an argument
                if style_func.__code__.co_argcount == 2:
                    style = style_func(cell, row)
                else:
                    style = style_func(cell)
                if style:
                    aligned_cell = self.pc.apply_style(style, aligned_cell)
                else:
                    if default_column_styles and col_idx in default_column_styles:
                        # Apply column-specific styles if provided
                        aligned_cell = self.pc.apply_style(default_column_styles[col_idx], aligned_cell)
            #elif default_column_styles and col_idx in default_column_styles:
                #aligned_cell = self.pc.apply_style(default_column_styles[col_idx], aligned_cell)
            elif default_column_styles and col_idx in default_column_styles:
                # Apply column-specific styles if provided
                aligned_cell = self.pc.apply_style(default_column_styles[col_idx], aligned_cell)
            elif cell_style:
                if isinstance(cell_style, list):
                    # Apply alternating styles based on the row index
                    style_to_apply = cell_style[0] if row_idx % 2 == 1 else cell_style[1]
                    aligned_cell = self.pc.apply_style(style_to_apply, aligned_cell)
                else:
                    aligned_cell = self.pc.apply_style(cell_style, aligned_cell)

        return aligned_cell


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
                       specific_headers: Union[Dict[str, Callable[[Any, List[Any], int, int, int], str]], str, None] = None,
                       cell_style: Optional[Union[str, List[str]]] = None,
                       target_text_box: bool = False,
                       conditional_style_functions: Optional[Dict[str, Callable[[Any], Optional[str]]]] = None,
                       double_space: bool = False,
                       use_styles: bool = True,
                       ephemeral: bool = False,
                       append_newline: bool = False,
                       ) -> str:

        """
        Generates a table with optional styling and alignment as a string.

        :param table_data: A list of lists representing the rows of the table.
        :param table_name: The name of the table (used for storage and reference).
        :param show_table_name: Whether to display the table name as a title.
        :param table_style: The style to apply to the entire table.
        :param border_char: Character used for table borders.
        :param col_sep: Column separator string.
        :param border_style: Style name for the table borders.
        :param col_sep_style: Style name for the column separators.
        :param header_style: Style name for the header row.
        :param header_column_styles: A dictionary mapping column indices to style names for the header row.
        :param col_alignments: A list of strings ('left', 'center', 'right') for column alignments.
        :param default_column_styles: A dictionary mapping column indices to style names for data cells.
        :param cell_style: Style name or list of styles for the table cells.
        :param target_text_box: Whether to target a specific text box (used in some rendering contexts).
        :param conditional_style_functions: A dictionary defining conditional styles based on cell values.
        :param double_space: Whether to double-space the table rows.
        :param use_styles: Whether to use styles (True) or plain text (False).
        :param ephemeral: If True, the table is not stored for future updates.
        :param append_newline: If True, adds a newline character at the end of the table string.
        :return: A string representing the formatted table.
        """


        if use_styles:
            styled_col_sep = self.pc.apply_style(col_sep_style, col_sep) if col_sep_style else col_sep
        else:
            styled_col_sep = self.pc.apply_color(col_sep_style, col_sep) if col_sep_style else col_sep

        # Step 1: Automatic Column Sizing
        max_col_lengths = [0] * len(table_data[0])
        for row in table_data:
            for i, cell in enumerate(row):
                if isinstance(cell, BoundCell):
                    cell = cell.get_value()
                cell_length = len(str(cell))
                max_col_lengths[i] = max(max_col_lengths[i], cell_length)

        # Step 2: Prepare Table Output
        table_output = []
        header = table_data[0]

        # If `specific_headers` is a string, retrieve the corresponding dictionary from `self.specific_headers`
        if isinstance(specific_headers, str):
            specific_headers = self.specific_headers.get(specific_headers, {})

        # Collect formatting parameters to store later
        format_params = {
            "col_alignments": col_alignments,
            "col_sep": col_sep,
            "col_sep_style": col_sep_style,
            "header_style": header_style,
            "header_column_styles": header_column_styles,
            "default_column_styles": default_column_styles,
            "specific_headers": specific_headers,
            "cell_style": cell_style,
            "conditional_style_functions": conditional_style_functions,
            "use_styles": use_styles,
            "target_text_box": target_text_box,
        }

        # Process each row
        for row_idx, row in enumerate(table_data):
            aligned_row = []
            for col_idx, cell in enumerate(row):
                if isinstance(cell, BoundCell):
                    cell = cell.get_value()
                aligned_cell = self.format_cell(cell, row, row_idx, col_idx, max_col_lengths, header, format_params)
                aligned_row.append(aligned_cell)

            # Create a row string and add to table output
            if target_text_box:
                row_str = self.pc.apply_style(col_sep_style, col_sep.lstrip()) + styled_col_sep.join(aligned_row) + self.pc.apply_style(col_sep_style, col_sep.rstrip())
            else:
                row_str = styled_col_sep + styled_col_sep.join(aligned_row) + styled_col_sep
            table_output.append(row_str)

        # Step 3: Generate Borders and Assemble Table
        table_lines = []
        line_number = 0  # To keep track of line numbers

        # Generate border line
        #table_str = ""
        #border_line = ""  # Initialize border_line to ensure it always has a value
        if border_style:
            border_length = sum(max_col_lengths) + len(max_col_lengths) * len(col_sep) + len(col_sep) - 2
            border_line = self.pc.apply_style(border_style, border_char * border_length)
            table_lines.append(border_line)
            line_number += 1

        # Add table name
        if show_table_name and table_name:
            centered_table_name = self.pc.apply_style(self.title_style, table_name.center(border_length))
            table_lines.append(centered_table_name)
            line_number += 1
            if border_style:
                table_lines.append(border_line)
                line_number += 1

        # Add header row
        table_lines.append(table_output[0])
        line_number += 1

        # Add header-data separator
        if border_style:
            table_lines.append(border_line)
            line_number += 1

        # Record the line number where data rows start
        data_start_line = line_number

        # Add data rows
        for i in range(1, len(table_output)):
            table_lines.append(table_output[i])
            line_number += 1
            if double_space:
                table_lines.append("")
                line_number += 1

        # Add closing border
        if border_style:
            table_lines.append(border_line)
            line_number += 1

        # Combine lines into a single string
        table_str = "\n".join(table_lines)

        # Append newline if parameter is True
        if append_newline:
            table_str += "\n"

        # Check if the table should be stored
        if table_name and not ephemeral:
            self.tables[table_name] = {
                "data": table_data,
                "generated_table": table_str,  # The final table output string
                "data_start_line": data_start_line,
                "format_params": format_params,
                "max_col_lengths": max_col_lengths,
                "border_length": border_length,
                "border_line": border_line,
                "bound": True,
            }

        return table_str



    @staticmethod
    def resolve_bound_instances(table_data):
        return [
            [
                cell.get_value() if isinstance(cell, BoundCell) else cell
                for cell in row
            ]
            for row in table_data
        ]


    def get_cursor_position(self, row_idx: int, col_idx: int, max_col_lengths: List[int], col_sep: str = " | ", starting_line: int = 0, target_text_box: bool = False) -> str:
        """
        Calculate the cursor position for a specific cell in the table.
        """
        x = 1  # Start from column 1
        if target_text_box:
            x += len(col_sep.lstrip())
        else:
            x += len(col_sep)  # Account for initial column separator

        # Calculate x position
        for idx in range(col_idx):
            x += max_col_lengths[idx] + len(col_sep)

        #y = starting_line + row_idx + 1  # Adjust for zero-based index
        y = starting_line + row_idx

        position = f"\033[{y};{x}H"

        self.debug(f"Calculated cursor position: {position} (row={row_idx}, col={col_idx})")

        return position


    @staticmethod
    def visible_length(s):
        return len(ANSI_ESCAPE.sub('', s))



    def refresh_bound_table(self, table_name: str) -> None:
        """
        Refreshes a bound table by updating only changed cells in-place.
        """
        if table_name not in self.tables or not self.tables[table_name]["bound"]:
            raise ValueError(f"Table '{table_name}' is not a bound table.")

        # Retrieve stored data and parameters
        table_info = self.tables[table_name]
        table_data = table_info["data"]
        previous_data = self.previous_values[table_name]
        data_start_line = table_info["data_start_line"]
        format_params = table_info.get('format_params', {})
        max_col_lengths = table_info["max_col_lengths"]
        col_sep = format_params.get('col_sep', " | ")
        target_text_box = format_params.get('target_text_box', False)

        # Resolve BoundCell instances
        resolved_data = self.resolve_bound_instances(table_data)

        # Get header row
        header = resolved_data[0]

        # Compare and update cells
        for row_idx, row in enumerate(resolved_data):
            for col_idx, cell in enumerate(row):
                new_value = str(cell)
                if new_value != previous_data[row_idx][col_idx]:
                    # Format cell
                    aligned_cell = self.format_cell(cell, row, row_idx, col_idx, max_col_lengths, header, format_params)

                    # Calculate cursor position
                    cursor_position = self.get_cursor_position(row_idx, col_idx, max_col_lengths, col_sep, data_start_line, target_text_box)

                    # Move cursor to position
                    print(cursor_position, end='')

                    # **Clear the cell area**
                    print(' ' * max_col_lengths[col_idx], end='', flush=True)

                    # Calculate the visible length of the styled cell
                    #cell_visible_length = self.visible_length(aligned_cell)

                    # Clear the cell area
                    #print(' ' * cell_visible_length, end='', flush=True)

                    # Move cursor back to start of cell
                    print(cursor_position, end='')

                    # Print updated cell content
                    print(aligned_cell, end='')

                    # Update previous data
                    previous_data[row_idx][col_idx] = new_value

                    """
                    # Move cursor and print updated cell
                    print(cursor_position + aligned_cell, end='')

                    # Update previous data
                    previous_data[row_idx][col_idx] = new_value
                    """

        print(flush=True)


    def add_bound_table(self, **kwargs) -> str:
        """
        Store a table with bound cells in self.tables, allowing real-time updates.
        """
        # Extract table_data from kwargs
        table_data = kwargs.pop('table_data', None)
        original_table_data = table_data  # Keep the original data with BoundCell instances

        # Resolve BoundCell instances for initial display
        if table_data is not None:
            resolved_data = self.resolve_bound_instances(table_data)
            kwargs['table_data'] = resolved_data

        formatted_table = self.generate_table(**kwargs)
        table_name = kwargs.get('table_name', None)

        # Ensure table_name is provided
        if table_name is None:
            raise ValueError("table_name must be provided when adding a bound table.")

        # Store the original table_data (with BoundCell instances)
        self.tables[table_name]["data"] = original_table_data  # Update the data with BoundCells

        # Initialize previous values with the resolved data
        self.previous_values[table_name] = [
            [str(cell) for cell in row]
            for row in resolved_data
        ]

        return formatted_table



    def live_update(self, table_name: str, update_callback: Callable[[], List[List[Any]]], interval: float = 1.0):
        """
        Creates a live-updating table that refreshes at a specified interval.

        Args:
            table_name (str): The name of the table to update.
            update_callback (Callable): A function that returns updated table data.
            interval (float): Time in seconds between updates.
        """
        if table_name not in self.tables:
            raise ValueError(f"Table '{table_name}' not found in TableManager.")

        try:
            while True:
                # Fetch the latest table data
                self.tables[table_name]["data"] = update_callback()

                # Clear the previous output
                os.system('clear')
                print(self.generate_table(self.tables[table_name]["data"], table_name=table_name))

                # Wait before updating again
                time.sleep(interval)
        except KeyboardInterrupt:
            print("Live update terminated.")















