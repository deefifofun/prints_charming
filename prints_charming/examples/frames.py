
import inspect
from typing import Dict, List, Optional, Tuple
from prints_charming import (
    PrintsCharming,
    FrameBuilder,
    TableManager
)




styled_strings = {
    "vgreen": ["Hello, world!", "string", "Connected", "Loaded", "Monitor", "ABOVE THRESHOLD", "wss://advanced-trade-ws.coinbase.com", "Starting", "True", "C++"],
    "green": ["apple"],
    "vred": ["Error", "Failed", "None", "Skipping.", "Canceling", "Canceled", "Hobbies", "Skills", "False"],
    "blue": ["CoinbaseWebsocketClient", "server", "Python"],
    "yellow": ["1", "returned", "Flask", "Some", ],
    "vyellow": ["File modified:", "File modified AGAIN", "subscribed", "=", "JavaScript"],
    "magenta": ["within 10 seconds.", "how", "React", "this is a test"],
    "cyan": ["|", "#", "are", "your", "Project Management System"],
    "orange": ["New Message!", "Prints", "Software Developer", "Prince Charming"],
    "purple": ["My color is purple", "Reading", "a normal different purple styled phrase and additionally"],
    "purple_dgray_bg": ["purple phrase with same bg_color"],
    "purple_dgray_bg_reverse": ["a normal different purple styled phrase with same bg_color but reverse"],
    "test_color_red_bg_dgray": ["new", "a normal styled phrase", "'test_color_red_bg_dgray' (style)"],
    "test_color_red_bg_dgray_reverse": ["new_reverse", "a reverse styled phrase"],
    "conceal": ["conceal1", "conceal2 is a phrase"],
    # Uncomment the next line to hide API keys or sensitive information
    # "conceal": [os.environ[key] for key in os.environ if "API" in key],
}


def get_pretty_caller_function_name(start="===", end="===", sep=' ', nl=False) -> Optional[str]:
    """
    Retrieves a formatted string containing the name of the caller function.

    Returns:
        Optional[str]: Formatted caller function name or None if not available.
    """
    # Get the current frame, then the caller's frame
    stack = inspect.stack()
    if len(stack) > 2:  # Ensure there is a caller
        caller_frame = stack[1]
        start_sep = sep if start else ''
        end_sep = sep if end else ''
        if nl:
            if nl is bool:
                nl = '\n'
        else:
            nl = ''
        return f"{start}{start_sep}{caller_frame.function}{end_sep}{end}{nl}"
    return None




def formatted_text_box_stuff(pc, builder):
    pc.print2(f"{get_pretty_caller_function_name()}", start='\n', end='\n', color='orange', italic=True, bold=True, fill_to_end=True if pc.default_bg_color else None)

    horiz_border_top, vert_border_left, vert_border_inner, vert_border_right, horiz_border_bottom = builder.build_styled_border_box(border_top_style='purple',
                                                                                                                                    border_bottom_style='orange',
                                                                                                                                    border_left_style='orange',
                                                                                                                                    border_inner_style='orange',
                                                                                                                                    border_right_style='purple')

    purple_horiz_border = pc.apply_style('purple', builder.horiz_border)
    orange_horiz_border = pc.apply_style('orange', builder.horiz_border)

    purple_vert_border = builder.vert_padding + pc.apply_style('purple', builder.vert_border)
    orange_vert_border = pc.apply_style('orange', builder.vert_border) + builder.vert_padding

    available_width = builder.get_available_width()

    title = 'Prints Charming'
    subtitle = 'Hope you find the user guide helpful'


    title_center_aligned = pc.apply_style('vgreen', builder.align_text(title, available_width, 'center'))
    subtitle_center_aligned = pc.apply_style('white', builder.align_text(subtitle, available_width, 'center'))


    print(purple_horiz_border)
    print(f'{orange_vert_border}{title_center_aligned}{purple_vert_border}')
    print(f'{orange_vert_border}{subtitle_center_aligned}{purple_vert_border}')
    print(f'{orange_horiz_border}\n')

    title_left_aligned = pc.apply_style('vgreen', builder.align_text(title, available_width, 'left'))
    subtitle_right_aligned = pc.apply_style('white', builder.align_text(subtitle, available_width, 'right'))

    print(purple_horiz_border)
    print(f'{orange_vert_border}{title_left_aligned}{purple_vert_border}')
    print(f'{orange_vert_border}{subtitle_right_aligned}{purple_vert_border}')
    print(f'{orange_horiz_border}\n')

    title_right_aligned = pc.apply_style('vgreen', builder.align_text(title, available_width, 'right'))
    subtitle_left_aligned = pc.apply_style('white', builder.align_text(subtitle, available_width, 'left'))

    print(purple_horiz_border)
    print(f'{orange_vert_border}{title_right_aligned}{purple_vert_border}')
    print(f'{orange_vert_border}{subtitle_left_aligned}{purple_vert_border}')
    print(f'{orange_horiz_border}\n\n')

    print(horiz_border_top)

    center_padding = " ".center(available_width)
    empty_line_with_borders = f"{vert_border_left}{center_padding}{vert_border_right}"
    print(empty_line_with_borders)
    print(empty_line_with_borders)

    left_open_border = (" " * builder.vert_width) + builder.vert_padding
    naked_right_text = "Prints Charming".rjust(available_width)
    print(f"{left_open_border}{naked_right_text}{vert_border_right}")

    left_open_border = (" " * builder.vert_width) + builder.vert_padding
    right_open_border = builder.vert_padding + (" " * builder.vert_width)
    naked_right_text = "Prints Charming".rjust(available_width)

    print(f"{left_open_border}{naked_right_text}{right_open_border}")
    print(f"{left_open_border}{naked_right_text}{vert_border_right}")

    naked_left_text = "Prints Charming"
    print(f"{vert_border_left}{naked_left_text}")

    centered_text = "Prints Charming".center(available_width)
    centered_subtext = "Hope you find the user guide helpful".center(available_width)
    left_text = "Prints Charming".ljust(available_width)
    left_subtext = "Hope you find the user guide helpful".ljust(available_width)
    right_text = "Prints Charming".rjust(available_width)
    right_subtext = "Hope you find the user guide helpful".rjust(available_width)
    print(f'{vert_border_left}{centered_text}{vert_border_right}')
    print(f'{vert_border_left}{centered_subtext}{vert_border_right}')
    print(f'{vert_border_left}{left_text}{vert_border_right}')
    print(f'{vert_border_left}{left_subtext}{vert_border_right}')
    print(f'{vert_border_left}{right_text}{vert_border_right}')
    print(f'{vert_border_left}{right_subtext}{vert_border_right}')
    print(f'{horiz_border_bottom}\n')

    one_col_text = 'center aligned single col'
    two_col_aligned_text_tuple = ('left aligned double col', 'right aligned double col')
    three_col_text_tuple = ('column_1', 'column_2', 'column_3')

    one_col_string = pc.apply_style('vgreen', builder.align_text(one_col_text, available_width, align='center'))
    two_col_strings_centered = builder.align_strings(['center aligned double col', 'center aligned double call'], available_width, styles=['purple', 'orange'])
    two_col_strings_hug_borders = builder.align_strings(['left aligned double col', 'right aligned double col'], available_width, styles=['purple', 'orange'],
                                                        alignments=['left', 'right'])
    two_col_strings_hug_left = builder.align_strings(['left aligned double col', 'left aligned double col'], available_width, styles=['purple', 'orange'],
                                                     alignments=['left', 'left'])
    two_col_strings_hug_right = builder.align_strings(['right aligned double col', 'right aligned double col'], available_width, styles=['purple', 'orange'],
                                                      alignments=['right', 'right'])

    three_col_strings_centered = builder.align_strings(three_col_text_tuple, available_width, styles=['purple', 'vgreen', 'orange'])
    three_col_strings_mixed = builder.align_strings(three_col_text_tuple, available_width, styles=['purple', 'vgreen', 'orange'], alignments=['left', 'center', 'right'])

    print(purple_horiz_border)
    print(f'{orange_vert_border}{one_col_string}{purple_vert_border}')
    print(f'{orange_vert_border}{two_col_strings_hug_borders}{purple_vert_border}')
    print(f'{orange_vert_border}{two_col_strings_centered}{purple_vert_border}')
    print(f'{orange_vert_border}{two_col_strings_hug_left}{purple_vert_border}')
    print(f'{orange_vert_border}{two_col_strings_hug_right}{purple_vert_border}')
    print(f'{orange_vert_border}{three_col_strings_centered}{purple_vert_border}')
    print(f'{orange_vert_border}{three_col_strings_mixed}{purple_vert_border}')
    print(f'{orange_horiz_border}\n\n\n\n')

    pc.printnl()


def border_boxed_text22(pc, builder):
    pc.print2(f"{get_pretty_caller_function_name()}", start='\n', end='\n', color='orange', italic=True, bold=True, fill_to_end=True if pc.default_bg_color else None)

    texts = [
        ['Row 1, Column 1, Centered'],
        [],
        ['Row 2, Column 1', 'Row 2, Column 2'],
        [],
        ['Row 3, Column 1', 'Row 3, Column 2', 'Row 3, Column 3'],
        [],
        ['col1', 'col2', 'col3', 'col4', 'col5', 'col6', 'col7', 'col8', 'col9', 'col10', 'col11', 'col12', 'col13', 'col14\ncell\ncell\ncell\ncell\ncell\ncell\ncell\ncell', 'col15',
         "col16\nHere we go multiple line wrapping at it's fucking finest!"]
    ]

    builder.print_border_boxed_text22(
        texts=texts,
        text_styles=[
            'red',
            [],
            ['green', 'orange'],
            [],
            ['green', 'orange', 'red'],
            [],
            'green',
        ],
        alignments=[
            'center',
            [],
            ['center', 'center'],
            [],
            ['center', 'center', 'center'],
            [],
            'center'
        ],
        style='blue',
        border_top=True,
        border_bottom=True,
        border_left=True,
        border_right=True,
        border_inner=True,
        match_column_heights=False,
    )
    pc.printnl()


def border_boxed_text2(pc, builder):
    pc.print2(f"{get_pretty_caller_function_name()}", start='\n', end='\n', color='orange', italic=True, bold=True, fill_to_end=True if pc.default_bg_color else None)

    info_table = [
        ["Status", "Action"],
        ["Toggled", "Expansion"]
    ]
    table_str = tm.generate_table(info_table, table_name="toggle_info", show_table_name=True, border_style="vblue", target_text_box=True)

    border_top, border_left, border_inner, border_right, border_bottom = builder.build_styled_border_box(style='blue')

    builder.print_border_boxed_table(table_str, border_top, border_left, border_right, border_bottom, text_align='left')


    texts = [
        [table_str],
        [],
        ['Row 2, Column 1', 'Row 2, Column 2'],
        [],
        ['Row 3, Column 1', 'Row 3, Column 2', 'Row 3, Column 3'],
        [],
        ['col1', 'col2', 'col3', 'col4', 'col5', 'col6', 'col7', 'col8', 'col9', 'col10', 'col11', 'col12', 'col13', 'col14', 'col15', "col16\nHere we go multiple line wrapping at it's fucking finest!"]
    ]

    builder.print_border_boxed_text2(
        texts=texts,
        text_styles=[
            'red',
            [],
            ['green', 'orange'],
            [],
            ['green', 'orange', 'red'],
            [],
            'green',
        ],
        alignments=[
            'center',
            [],
            ['center', 'center'],
            [],
            ['center', 'center', 'center'],
            [],
            'center'
        ],
        style='blue',
        border_top=True,
        border_bottom=True,
        border_left=True,
        border_right=True,
        border_inner=True
    )
    pc.printnl()



def multi_row_mixed_cols(pc, builder):
    pc.print2(f"{get_pretty_caller_function_name()}", start='\n', end='\n', color='orange', italic=True, bold=True, fill_to_end=True if pc.default_bg_color else None)

    texts = [
        ['Row 1, Column 1, Centered'],
        [],
        ['Row 2, Column 1', 'Row 2, Column 2'],
        [],
        ['Row 3, Column 1', 'Row 3, Column 2', 'Row 3, Column 3'],
        [],
        ['col1', 'col2', 'col3', 'col4', 'col5', 'col6', 'col7', 'col8', 'col9', 'col10', 'col11', 'col12', 'col13', 'col14', 'col15', 'col16']
    ]

    builder.print_border_boxed_text1(
        texts=texts,
        text_styles=[
            'red',
            [],
            ['green', 'orange'],
            [],
            ['green', 'orange', 'red'],
            [],
            'green',
        ],
        alignments=[
            'center',
            [],
            ['center', 'center'],
            [],
            ['center', 'center', 'center'],
            [],
            'center'
        ],
        style='blue',
        border_top=True,
        border_bottom=True,
        border_left=True,
        border_right=True,
        border_inner=True
    )
    pc.printnl()


def three_col_box(pc, builder):
    pc.print2(f"{get_pretty_caller_function_name()}", start='\n', end='\n', color='orange', italic=True, bold=True, fill_to_end=True if pc.default_bg_color else None)

    texts = [['left center aligned text', 'middle center aligned text', 'right center aligned text']]

    builder.print_border_boxed_text1(
        texts=texts,
        text_styles=[['green', 'orange', 'red']],
        alignments=[['center', 'center', 'center']],
        style='blue',
        border_top=True,
        border_bottom=True,
        border_left=True,
        border_right=True,
        border_inner=True
    )
    pc.printnl()


def two_col_box(pc, builder):
    pc.print2(f"{get_pretty_caller_function_name()}", start='\n', end='\n', color='orange', italic=True, bold=True, fill_to_end=True if pc.default_bg_color else None)

    texts = [['left center aligned text', 'right center aligned text']]

    builder.print_border_boxed_text1(
        texts=texts,
        text_styles=[['green', 'orange']],
        alignments=[['center', 'center']],
        style='blue',
        border_top=True,
        border_bottom=True,
        border_left=True,
        border_right=True,
        border_inner=True
    )
    pc.printnl()


def single_col_box(pc, builder):
    pc.print2(f"{get_pretty_caller_function_name()}", start='\n', end='\n', color='orange', italic=True, bold=True, fill_to_end=True if pc.default_bg_color else None)

    texts = ['center aligned text']

    builder.print_border_boxed_text1(
        texts=texts,
        text_styles='green',
        alignments='center',
        style='blue',
        border_top=True,
        border_bottom=True,
        border_left=True,
        border_right=True,
        border_inner=False
    )
    pc.printnl()


def border_boxed_text1(pc, builder):
    single_col_box(pc, builder)
    two_col_box(pc, builder)
    three_col_box(pc, builder)
    multi_row_mixed_cols(pc, builder)



def styled_border_box2(pc, builder):
    pc.print2(f"{get_pretty_caller_function_name()}", start='\n', end='\n', color='orange', italic=True, bold=True, fill_to_end=True if pc.default_bg_color else None)

    border_top, border_left, border_inner, border_right, border_bottom = builder.build_styled_border_box(style='blue')

    centered_text = builder.align_text('center aligned text')
    bordered_text = f'{border_left}{centered_text}{border_right}'
    print(border_top)
    print(bordered_text)

    blank_line = builder.align_text(' ')
    left_border = border_left if border_left else ''
    right_border = border_right if border_right else ''
    print(f'{left_border}{blank_line}{right_border}')

    # Get available width including 1 inner border
    available_width_1_inner = builder.get_available_width(num_inner_borders=1)

    # Adjust widths for left and right text
    left_text_width = available_width_1_inner // 2
    right_text_width = available_width_1_inner - left_text_width  # Remaining width for right text

    # Align text within the calculated widths
    left_text = builder.align_text('left aligned text', align='center', available_width=left_text_width)
    right_text = builder.align_text('right aligned text', align='center', available_width=right_text_width)

    print(border_top)
    bordered_text_inner_1 = f'{border_left}{left_text}{border_inner}{right_text}{border_right}'
    print(bordered_text_inner_1)





    print(border_bottom)
    pc.printnl()





def sbb2(pc):
    pc.print2(f"{get_pretty_caller_function_name()}", start='\n', end='\n', color='orange', italic=True, bold=True, fill_to_end=True if pc.default_bg_color else None)

    builder2 = FrameBuilder(pc=pc, horiz_char='|', vert_char='|', vert_width=2, vert_padding=1, inner_char='|', inner_width=2, inner_padding=1)
    table_manager = TableManager()

    # Box1
    box1_top, box1_left, box1_inner, box1_right, box1_bottom = builder2.build_unstyled_border_box()

    table_data = [
        ["Name", "Age", "Occupation"],
        ["Prince Charming", 25, "Prince"],
        ["Cinderella", 18, "Princess"],
        ["Anastasia", 22, "Socialite"],
        ["Drizella", 20, "Socialite"],
        ["Ariel", 16, "Mermaid"],
        ["John Smith", 17, "Normie"]
    ]

    less_simple_table = table_manager.generate_table(table_data=table_data,
                                                     header_style="magenta",
                                                     border_style="vgreen",
                                                     col_sep_style="vgreen",
                                                     target_text_box=True,
                                                     cell_style=["orange", "purple"],
                                                     ephemeral=True,
                                                     append_newline=True,
                                                     )
    print(less_simple_table)

    builder2.print_border_boxed_tables2([less_simple_table, less_simple_table, less_simple_table, less_simple_table],
                                       None, box1_left, box1_right, None,
                                       table_alignments=['center', 'center', 'center', 'center'])

    print(f'length box1_top: {len(box1_top)}')
    print(f'length box1_left: {len(box1_left)}')
    print(f'length box1_inner: {len(box1_inner)}')
    print(f'length box1_right: {len(box1_right)}')
    print(f'length box1_bottom: {len(box1_bottom)}')

    box1_top_styled = pc.apply_style('blue', box1_top)
    box1_left_styled = pc.apply_style('blue', box1_left)
    box1_inner_styled = pc.apply_style('blue', box1_inner)
    box1_right_styled = pc.apply_style('blue', box1_right)
    box1_bottom_styled = pc.apply_style('blue', box1_bottom)

    box1_available_width = builder2.get_available_width()
    print(f'box1_available_width: {box1_available_width}')
    box1_blank_line = builder2.align_text(" ", available_width=box1_available_width)
    box1_center_aligned_text = builder2.align_text("center_aligned_text", available_width=box1_available_width)

    box2_top = builder2.align_text(box1_top[:box1_available_width])
    box2_left = box1_left
    box2_inner = box1_inner
    box2_right = box1_right
    box2_bottom = builder2.align_text(box1_bottom[:box1_available_width])

    print(f'length box2_top: {len(box2_top)}')
    print(f'length box2_left: {len(box2_left)}')
    print(f'length box2_inner: {len(box2_inner)}')
    print(f'length box2_right: {len(box2_right)}')
    print(f'length box2_bottom: {len(box2_bottom)}')

    box2_top_styled = pc.apply_style('orange', box2_top)
    box2_left_styled = pc.apply_style('orange', box2_left)
    box2_inner_styled = pc.apply_style('orange', box2_inner)
    box2_right_styled = pc.apply_style('orange', box2_right)
    box2_bottom_styled = pc.apply_style('orange', box2_bottom)

    # Get available width taking into account 1 inner border, box1_left, and box1_right
    box2_not_nested_available_width = builder2.get_available_width(num_inner_borders=1)
    print(f'self.available_width: {builder2.available_width}')
    print(f'box2_not_nested_available_width: {box2_not_nested_available_width}')
    box2_available_width = box2_not_nested_available_width - len(box1_left) - len(box1_right)
    print(f'box2_available_width: {box2_available_width}')

    # Adjust widths for left and right text
    left_text_width = box2_available_width // 2
    right_text_width = box2_available_width - left_text_width  # Remaining width for right text

    # Box2 blank line
    box2_left_blank_line = builder2.align_text(" ", available_width=left_text_width)
    box2_right_blank_line = builder2.align_text(" ", available_width=right_text_width)

    # Align text within the calculated widths for box2 line1
    box2_left_text_line1 = builder2.align_text('center aligned text', available_width=left_text_width)
    box2_right_text_line1 = builder2.align_text('center aligned text', available_width=right_text_width)

    # Align text within the calculated widths for box2 line2
    inside_of_box2_first_col = "box3 will have 2 columns and will be inserted right here and therefore nested here within box2 similarly to how box2 here is nested inside of box1"
    inside_of_box2_first_col_text_lines = builder2.split_text_to_lines(inside_of_box2_first_col, left_text_width)

    inside_of_box2_second_col = "box4 will have 2 columns and will be inserted right here and therefore nested here within box2 similarly to how box2 here is nested inside of box1."
    inside_of_box2_second_col_text_lines = builder2.split_text_to_lines(inside_of_box2_second_col, right_text_width)
    align_texts = {}
    align_texts["left"] = []
    align_texts["right"] = []
    for line in inside_of_box2_first_col_text_lines:
        aligned_text = builder2.align_text(line, left_text_width, "left")
        align_texts['left'].append(aligned_text)
    for line in inside_of_box2_second_col_text_lines:
        aligned_text = builder2.align_text(line, right_text_width, "left")
        align_texts['right'].append(aligned_text)


    # for tables left
    table_strs_left = [less_simple_table, less_simple_table]
    table_alignments_left = ['center', 'center']
    num_tables = len(table_strs_left)
    section_left_width = (left_text_width - (num_tables - 1)) // num_tables

    table_lines_left_list = [table_str.split("\n") for table_str in table_strs_left]
    max_lines_left = max(len(table_lines) for table_lines in table_lines_left_list)
    for table_lines in table_lines_left_list:
        table_lines += [''] * (max_lines_left - len(table_lines))




    # for tables right
    table_strs_right = [less_simple_table, less_simple_table]
    table_alignments_right = ['center', 'center']
    num_tables = len(table_strs_right)
    section_right_width = (right_text_width - (num_tables - 1)) // num_tables

    table_lines_right_list = [table_str.split("\n") for table_str in table_strs_right]
    max_lines_right = max(len(table_lines) for table_lines in table_lines_right_list)
    for table_lines in table_lines_right_list:
        table_lines += [''] * (max_lines_right - len(table_lines))





    # Align text within the calculated widths for box2 line3
    box2_left_text_line3 = builder2.align_text('right aligned text', align='right', available_width=left_text_width)
    box2_right_text_line3 = builder2.align_text('left aligned text', align='left', available_width=right_text_width)

    # Align text within the calculated widths for box2 lines 4-10
    box2_left_text_line4 = builder2.align_text(' ', available_width=left_text_width)
    box2_right_text_line4 = builder2.align_text(' ', available_width=right_text_width)


    lines = []

    # Box1 top
    lines.append(box1_top_styled)

    # Box1 blank line, centered text, blank_line
    lines.append(f'{box1_left_styled}{box1_blank_line}{box1_right_styled}')
    lines.append(f'{box1_left_styled}{box1_center_aligned_text}{box1_right_styled}')
    lines.append(f'{box1_left_styled}{box1_blank_line}{box1_right_styled}')

    # Box2 top
    lines.append(f'{box1_left_styled}{box2_top_styled}{box1_right_styled}')

    # Box2 blank line, centered_text, blank line
    lines.append(f'{box1_left_styled}{box2_left_styled}{box2_left_blank_line}{box2_inner_styled}{box2_right_blank_line}{box2_right_styled}{box1_right_styled}')
    lines.append(f'{box1_left_styled}{box2_left_styled}{box2_left_text_line1}{box2_inner_styled}{box2_right_text_line1}{box2_right_styled}{box1_right_styled}')
    lines.append(f'{box1_left_styled}{box2_left_styled}{box2_left_blank_line}{box2_inner_styled}{box2_right_blank_line}{box2_right_styled}{box1_right_styled}')





    for line_left, line_right in zip(align_texts['left'], align_texts['right']):
        lines.append(f'{box1_left_styled}{box2_left_styled}{line_left}{box2_inner_styled}{line_right}{box2_right_styled}{box1_right_styled}')

    lines.append(f'{box1_left_styled}{box2_left_styled}{box2_left_text_line4}{box2_inner_styled}{box2_right_text_line4}{box2_right_styled}{box1_right_styled}')
    lines.append(f'{box1_left_styled}{box2_left_styled}{box2_left_text_line4}{box2_inner_styled}{box2_right_text_line4}{box2_right_styled}{box1_right_styled}')
    lines.append(f'{box1_left_styled}{box2_left_styled}{box2_left_text_line4}{box2_inner_styled}{box2_right_text_line4}{box2_right_styled}{box1_right_styled}')
    lines.append(f'{box1_left_styled}{box2_left_styled}{box2_left_text_line4}{box2_inner_styled}{box2_right_text_line4}{box2_right_styled}{box1_right_styled}')
    lines.append(f'{box1_left_styled}{box2_left_styled}{box2_left_text_line4}{box2_inner_styled}{box2_right_text_line4}{box2_right_styled}{box1_right_styled}')
    lines.append(f'{box1_left_styled}{box2_left_styled}{box2_left_text_line4}{box2_inner_styled}{box2_right_text_line4}{box2_right_styled}{box1_right_styled}')
    lines.append(f'{box1_left_styled}{box2_left_styled}{box2_left_text_line4}{box2_inner_styled}{box2_right_text_line4}{box2_right_styled}{box1_right_styled}')

    for line_index_left, line_index_right in zip(range(max_lines_left), range(max_lines_right)):
        row_left = ""
        row_right = ""

        for table_index_left, table_lines_left in enumerate(table_lines_left_list):
            if line_index_left < len(table_lines_left):
                line_left = table_lines_left[line_index_left]
                stripped_line_left = builder2.strip_ansi_escape_sequences(line_left)
                text_align_left = table_alignments_left[table_index_left] if table_index_left < len(table_alignments_left) else 'left'
                row_left += builder2.align_text(stripped_line_left, section_left_width, text_align_left)


        for table_index_right, table_lines_right in enumerate(table_lines_right_list):
            if line_index_right < len(table_lines_right):
                line_right = table_lines_right[line_index_right]
                stripped_line_right = builder2.strip_ansi_escape_sequences(line_right)
                text_align_right = table_alignments_right[table_index_right] if table_index_right < len(table_alignments_right) else 'left'
                row_right += builder2.align_text(stripped_line_right, section_right_width, text_align_right)

        # Calculate padding and construct styled lines
        row_length_left = len(builder2.strip_ansi_escape_sequences(row_left))
        row_length_right = len(builder2.strip_ansi_escape_sequences(row_right))

        padding_needed_left = section_left_width - row_length_left
        padding_needed_right = section_right_width - row_length_right

        styled_line = (
            f"{box1_left_styled}{box2_left_styled}{row_left}"
            f"{box2_inner_styled}{row_right}{box2_right_styled}{box1_right_styled}"
        )
        lines.append(styled_line)


    lines.append(f'{box1_left_styled}{box2_bottom_styled}{box1_right_styled}')

    lines.append(f'{box1_left_styled}{box1_blank_line}{box1_right_styled}')
    lines.append(f'{box1_left_styled}{box1_center_aligned_text}{box1_right_styled}')
    lines.append(f'{box1_left_styled}{box1_blank_line}{box1_right_styled}')

    lines.append(box1_bottom_styled)

    for line in lines:
        print(line)

    pc.printnl()
    pc.printnl()
    pc.printnl()








def styled_border_box(pc, builder):
    pc.print2(f"{get_pretty_caller_function_name()}", start='\n', end='\n', color='orange', italic=True, bold=True, fill_to_end=True if pc.default_bg_color else None)

    """
    # Box1
    box1_top, box1_left, box1_inner, box1_right, box1_bottom = builder.build_styled_border_box(style='blue')

    box1_centered_text = builder.align_text('center aligned text')
    box1_bordered_text = f'{box1_left}{box1_centered_text}{box1_right}'
    print(box1_top)
    print(box1_bordered_text)
    print(box1_bottom)
    pc.printnl()

    # Get available width including 1 inner border
    available_width = builder.get_available_width(num_inner_borders=1)

    # Adjust widths for left and right text
    left_text_width = available_width // 2
    right_text_width = available_width - left_text_width  # Remaining width for right text

    # Align text within the calculated widths
    left_text = builder.align_text('left aligned text', align='center', available_width=left_text_width)
    right_text = builder.align_text('right aligned text', align='center', available_width=right_text_width)

    bordered_text = f'{box1_left}{left_text}{box1_inner}{right_text}{box1_right}'
    print(box1_top)
    print(bordered_text)
    print(box1_bottom)
    pc.printnl()


    # Get available width including 2 inner borders
    available_width = builder.get_available_width(num_inner_borders=2)
    section_width = available_width // 3
    leftover_space = available_width - (section_width * 3)

    # Adjust right text width to include leftover space
    left_text_width = section_width
    middle_text_width = section_width
    right_text_width = section_width + leftover_space

    # Align text for the second box
    left_text = builder.align_text('left aligned text', align='center', available_width=left_text_width)
    middle_text = builder.align_text('middle aligned text', align='center', available_width=middle_text_width)
    right_text = builder.align_text('right aligned text', align='center', available_width=right_text_width)

    # Construct and print the second bordered box
    bordered_text = (
        f"{box1_left}{left_text}{box1_inner}{middle_text}"
        f"{box1_inner}{right_text}{box1_right}"
    )
    print(box1_top)
    print(bordered_text)
    print(box1_bottom)
    pc.printnl()

    # Get available width including 3 inner borders
    available_width = builder.get_available_width(num_inner_borders=3)
    section_width = available_width // 4
    leftover_space = available_width - (section_width * 4)

    # Adjust right text width to include leftover space
    left_text_width = section_width
    middle_left_text_width = section_width
    middle_right_text_width = section_width
    right_text_width = section_width + leftover_space

    # Align text for the second box
    left_text = builder.align_text('left aligned text', align='center', available_width=left_text_width)
    middle_text_left = builder.align_text('middle left text', align='center', available_width=middle_left_text_width)
    middle_text_right = builder.align_text('middle right text', align='center', available_width=middle_right_text_width)
    right_text = builder.align_text('right aligned text', align='center', available_width=right_text_width)

    # Construct and print the second bordered box
    bordered_text = (
        f"{box1_left}{left_text}{box1_inner}{middle_text_left}{box1_inner}{middle_text_right}{box1_inner}{right_text}{box1_right}"
    )
    print(box1_top)
    print(bordered_text)
    print(box1_bottom)
    pc.printnl()
    pc.printnl()
    pc.printnl()
    """



    builder2 = FrameBuilder(pc=pc, horiz_char='|', vert_char='|', vert_width=2, vert_padding=1, inner_char='|', inner_width=2, inner_padding=1)

    # Box1
    box1_top, box1_left, box1_inner, box1_right, box1_bottom = builder2.build_unstyled_border_box()

    print(f'length box1_top: {len(box1_top)}')
    print(f'length box1_left: {len(box1_left)}')
    print(f'length box1_inner: {len(box1_inner)}')
    print(f'length box1_right: {len(box1_right)}')
    print(f'length box1_bottom: {len(box1_bottom)}')

    box1_top_styled = pc.apply_style('blue', box1_top)
    box1_left_styled = pc.apply_style('blue', box1_left)
    box1_inner_styled = pc.apply_style('blue', box1_inner)
    box1_right_styled = pc.apply_style('blue', box1_right)
    box1_bottom_styled = pc.apply_style('blue', box1_bottom)

    box1_available_width = builder2.get_available_width()
    print(f'box1_available_width: {box1_available_width}')
    box1_blank_line = builder2.align_text(" ", available_width=box1_available_width)
    box1_center_aligned_text = builder2.align_text("center_aligned_text", available_width=box1_available_width)

    box2_top = builder2.align_text(box1_top[:box1_available_width])
    box2_left = box1_left
    box2_inner = box1_inner
    box2_right = box1_right
    box2_bottom = builder2.align_text(box1_bottom[:box1_available_width])

    print(f'length box2_top: {len(box2_top)}')
    print(f'length box2_left: {len(box2_left)}')
    print(f'length box2_inner: {len(box2_inner)}')
    print(f'length box2_right: {len(box2_right)}')
    print(f'length box2_bottom: {len(box2_bottom)}')

    box2_top_styled = pc.apply_style('orange', box2_top)
    box2_left_styled = pc.apply_style('orange', box2_left)
    box2_inner_styled = pc.apply_style('orange', box2_inner)
    box2_right_styled = pc.apply_style('orange', box2_right)
    box2_bottom_styled = pc.apply_style('orange', box2_bottom)

    # Get available width taking into account 1 inner border, box1_left, and box1_right
    box2_not_nested_available_width = builder2.get_available_width(num_inner_borders=1)
    print(f'self.available_width: {builder2.available_width}')
    print(f'box2_not_nested_available_width: {box2_not_nested_available_width}')
    box2_available_width = box2_not_nested_available_width - len(box1_left) - len(box1_right)
    print(f'box2_available_width: {box2_available_width}')

    # Adjust widths for left and right text
    left_text_width = box2_available_width // 2
    right_text_width = box2_available_width - left_text_width  # Remaining width for right text

    # Box2 blank line
    box2_left_blank_line = builder2.align_text(" ", available_width=left_text_width)
    box2_right_blank_line = builder2.align_text(" ", available_width=right_text_width)

    # Align text within the calculated widths for box2 line1
    box2_left_text_line1 = builder2.align_text('center aligned text', available_width=left_text_width)
    box2_right_text_line1 = builder2.align_text('center aligned text', available_width=right_text_width)

    # Align text within the calculated widths for box2 line2
    box2_left_text_line2 = builder2.align_text('left aligned text', align='left', available_width=left_text_width)
    box2_right_text_line2 = builder2.align_text('right aligned text', align='right', available_width=right_text_width)

    # Align text within the calculated widths for box2 line3
    box2_left_text_line3 = builder2.align_text('right aligned text', align='right', available_width=left_text_width)
    box2_right_text_line3 = builder2.align_text('left aligned text', align='left', available_width=right_text_width)

    # Align text within the calculated widths for box2 lines 4-10
    box2_left_text_line4 = builder2.align_text(' ', available_width=left_text_width)
    box2_right_text_line4 = builder2.align_text(' ', available_width=right_text_width)

    lines = []
    lines.append(box1_top_styled)
    lines.append(f'{box1_left_styled}{box1_blank_line}{box1_right_styled}')
    lines.append(f'{box1_left_styled}{box1_center_aligned_text}{box1_right_styled}')
    lines.append(f'{box1_left_styled}{box1_blank_line}{box1_right_styled}')

    lines.append(f'{box1_left_styled}{box2_top_styled}{box1_right_styled}')
    lines.append(f'{box1_left_styled}{box2_left_styled}{box2_left_blank_line}{box2_inner_styled}{box2_right_blank_line}{box2_right_styled}{box1_right_styled}')
    lines.append(f'{box1_left_styled}{box2_left_styled}{box2_left_text_line1}{box2_inner_styled}{box2_right_text_line1}{box2_right_styled}{box1_right_styled}')
    lines.append(f'{box1_left_styled}{box2_left_styled}{box2_left_blank_line}{box2_inner_styled}{box2_right_blank_line}{box2_right_styled}{box1_right_styled}')
    lines.append(f'{box1_left_styled}{box2_left_styled}{box2_left_text_line2}{box2_inner_styled}{box2_right_text_line2}{box2_right_styled}{box1_right_styled}')
    lines.append(f'{box1_left_styled}{box2_left_styled}{box2_left_text_line3}{box2_inner_styled}{box2_right_text_line3}{box2_right_styled}{box1_right_styled}')
    lines.append(f'{box1_left_styled}{box2_left_styled}{box2_left_text_line4}{box2_inner_styled}{box2_right_text_line4}{box2_right_styled}{box1_right_styled}')
    lines.append(f'{box1_left_styled}{box2_left_styled}{box2_left_text_line4}{box2_inner_styled}{box2_right_text_line4}{box2_right_styled}{box1_right_styled}')
    lines.append(f'{box1_left_styled}{box2_left_styled}{box2_left_text_line4}{box2_inner_styled}{box2_right_text_line4}{box2_right_styled}{box1_right_styled}')
    lines.append(f'{box1_left_styled}{box2_left_styled}{box2_left_text_line4}{box2_inner_styled}{box2_right_text_line4}{box2_right_styled}{box1_right_styled}')
    lines.append(f'{box1_left_styled}{box2_left_styled}{box2_left_text_line4}{box2_inner_styled}{box2_right_text_line4}{box2_right_styled}{box1_right_styled}')
    lines.append(f'{box1_left_styled}{box2_left_styled}{box2_left_text_line4}{box2_inner_styled}{box2_right_text_line4}{box2_right_styled}{box1_right_styled}')
    lines.append(f'{box1_left_styled}{box2_left_styled}{box2_left_text_line4}{box2_inner_styled}{box2_right_text_line4}{box2_right_styled}{box1_right_styled}')



    lines.append(f'{box1_left_styled}{box2_bottom_styled}{box1_right_styled}')

    lines.append(f'{box1_left_styled}{box1_blank_line}{box1_right_styled}')
    lines.append(f'{box1_left_styled}{box1_center_aligned_text}{box1_right_styled}')
    lines.append(f'{box1_left_styled}{box1_blank_line}{box1_right_styled}')

    lines.append(box1_bottom_styled)

    for line in lines:
        print(line)

    pc.printnl()
    pc.printnl()
    pc.printnl()

    lines2 = []

    # Box1 top
    lines2.append(box1_top_styled)

    # Box1 blank line, centered text, blank line
    lines2.append(f'{box1_left_styled}{box1_blank_line}{box1_right_styled}')
    lines2.append(f'{box1_left_styled}{box1_center_aligned_text}{box1_right_styled}')
    lines2.append(f'{box1_left_styled}{box1_blank_line}{box1_right_styled}')

    # Box2 top
    lines2.append(f'{box1_left_styled}{box2_top_styled}{box1_right_styled}')

    # Box2 blank line, centered_text, blank line
    lines2.append(f'{box1_left_styled}{box2_left_styled}{box2_left_blank_line}{box2_inner_styled}{box2_right_blank_line}{box2_right_styled}{box1_right_styled}')
    lines2.append(f'{box1_left_styled}{box2_left_styled}{box2_left_text_line1}{box2_inner_styled}{box2_right_text_line1}{box2_right_styled}{box1_right_styled}')
    lines2.append(f'{box1_left_styled}{box2_left_styled}{box2_left_blank_line}{box2_inner_styled}{box2_right_blank_line}{box2_right_styled}{box1_right_styled}')






    lines2.append(f'{box1_left_styled}{box2_left_styled}{box2_left_text_line2}{box2_inner_styled}{box2_right_text_line2}{box2_right_styled}{box1_right_styled}')
    lines2.append(f'{box1_left_styled}{box2_left_styled}{box2_left_text_line3}{box2_inner_styled}{box2_right_text_line3}{box2_right_styled}{box1_right_styled}')
    lines2.append(f'{box1_left_styled}{box2_left_styled}{box2_left_text_line4}{box2_inner_styled}{box2_right_text_line4}{box2_right_styled}{box1_right_styled}')
    lines2.append(f'{box1_left_styled}{box2_left_styled}{box2_left_text_line4}{box2_inner_styled}{box2_right_text_line4}{box2_right_styled}{box1_right_styled}')
    lines2.append(f'{box1_left_styled}{box2_left_styled}{box2_left_text_line4}{box2_inner_styled}{box2_right_text_line4}{box2_right_styled}{box1_right_styled}')
    lines2.append(f'{box1_left_styled}{box2_left_styled}{box2_left_text_line4}{box2_inner_styled}{box2_right_text_line4}{box2_right_styled}{box1_right_styled}')
    lines2.append(f'{box1_left_styled}{box2_left_styled}{box2_left_text_line4}{box2_inner_styled}{box2_right_text_line4}{box2_right_styled}{box1_right_styled}')
    lines2.append(f'{box1_left_styled}{box2_left_styled}{box2_left_text_line4}{box2_inner_styled}{box2_right_text_line4}{box2_right_styled}{box1_right_styled}')
    lines2.append(f'{box1_left_styled}{box2_left_styled}{box2_left_text_line4}{box2_inner_styled}{box2_right_text_line4}{box2_right_styled}{box1_right_styled}')

    lines2.append(f'{box1_left_styled}{box2_bottom_styled}{box1_right_styled}')

    lines2.append(f'{box1_left_styled}{box1_blank_line}{box1_right_styled}')
    lines2.append(f'{box1_left_styled}{box1_center_aligned_text}{box1_right_styled}')
    lines2.append(f'{box1_left_styled}{box1_blank_line}{box1_right_styled}')

    lines2.append(box1_bottom_styled)

    for line in lines2:
        print(line)

    pc.printnl()






def border_boxed_text4(pc, builder):
    pc.print2(f"{get_pretty_caller_function_name()}", start='\n', end='\n', color='orange', italic=True, bold=True, fill_to_end=True if pc.default_bg_color else None)

    border_top, border_left, border_inner, border_right, border_bottom = builder.build_styled_border_box(style='blue')

    texts = [
        'First line of text',
        'Second line of text',
        'Third line of text',
        'Fourth line of text',
        'Fifth line of text',
        'Sixth line of text',
        'Seventh line of text',
        'invisible_text',
        "Eighth line of text, but this line is really really really long because i'm trying to make it split across multiple lines like not just split across one line, but i want it to have to split across multiple lines like atleast 3 lines but possibly even more lines because i want to see the text have to get split across multiple lines becasue thats the kind of test that this is. Also want to see what happens if i add multiple spaces like this                      between      some   of the      text. Wow oke here we go is that         it!"
    ]

    builder.print_border_boxed_text4(texts=texts, border_top=border_top, border_bottom=border_bottom, border_left=border_left, border_right=border_right)
    pc.printnl()


def border_boxed_text3(pc, builder):
    pc.print2(f"{get_pretty_caller_function_name()}", start='\n', end='\n', color='orange', italic=True, bold=True, fill_to_end=True if pc.default_bg_color else None)

    border_top, border_left, border_inner, border_right, border_bottom = builder.build_styled_border_box(style='blue')

    texts = [
        'First line of text',
        'Second line of text',
        'Third line of text',
        'Fourth line of text',
        'Fifth line of text',
        'Sixth line of text',
        'Seventh line of text',
        "Eighth line of text, but this line is really really really long because i'm trying to make it split across multiple lines like not just split across one line, but i want it to have to split across multiple lines like atleast 3 lines but possibly even more lines because i want to see the text have to get split across multiple lines becasue thats the kind of test that this is. Also want to see what happens if i add multiple spaces like this                      between      some   of the      text. Wow oke here we go is that         it!"
    ]

    builder.print_border_boxed_text3(texts=texts, border_top=border_top, border_bottom=border_bottom, border_left=border_left, border_right=border_right)
    pc.printnl()


def border_boxed_text(pc, builder):
    pc.print2(f"{get_pretty_caller_function_name()}", start='\n', end='\n', color='orange', italic=True, bold=True, fill_to_end=True if pc.default_bg_color else None)

    builder.print_border_boxed_text(text="Border Boxed Text", subtext="Subtext Border Boxed Text", all_borders_style='purple')
    pc.printnl()


def test_frame_builder(pc, builder):
    border_boxed_text(pc, builder)
    border_boxed_text3(pc, builder)
    border_boxed_text4(pc, builder)
    styled_border_box(pc, builder)
    sbb2(pc)
    styled_border_box2(pc, builder)
    border_boxed_text1(pc, builder)
    border_boxed_text2(pc, builder)
    border_boxed_text22(pc, builder)






def main():
    pc = PrintsCharming(styled_strings=styled_strings)
    builder = FrameBuilder(pc=pc, horiz_char=' ', vert_width=2, vert_padding=0, vert_char=' ')
    formatted_text_box_stuff(pc, builder)
    test_frame_builder(pc, builder)








if __name__ == '__main__':
    tm = TableManager()
    main()











