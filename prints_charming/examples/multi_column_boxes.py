import inspect
from typing import Optional

from prints_charming import (
    PStyle,
    PrintsCharming,
    FrameBuilder,
    TableManager,
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



def nested_boxes_test(pc, builder):
    pc.print2(f"{get_pretty_caller_function_name()}", start='\n', end='\n', color='orange', italic=True, bold=True, fill_to_end=True if pc.default_bg_color else None)

    boxes = {}
    """
    for level in range(1, 3):
        border_top, border_left, border_inner, border_right, border_bottom = builder.build_unstyled_border_box()
        boxes[level]['top'] = border_top
        boxes[level]['left'] = border_left
        boxes[level]['inner'] = border_inner
        boxes[level]['right'] = border_right
        boxes[level]['bottom'] = border_bottom
    """









def border_boxed_text2(pc, builder, tm):
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


def more_stuff(pc, builder, tm):
    pc.print2(f"{get_pretty_caller_function_name()}", start='\n', end='\n', color='orange', italic=True, bold=True, fill_to_end=True if pc.default_bg_color else None)

    solid_horiz_rule = builder.terminal_width * ' '
    avail_width = builder.get_available_width()

    structured_text = """
            Name: {name}
            Age: {age}
            Balance: {balance}
            Occupation: {occupation}

            Skills:
            - Python
            - JavaScript
            - C++

            Projects:
            1. Project Management System
               - Description: A web-based application to manage projects and tasks.
               - Technologies: Django, React, PostgreSQL

            2. E-commerce Platform
               - Description: An online store with payment integration.
               - Technologies: Flask, Angular, MySQL

            Hobbies:
            - Reading
            - Hiking
            - Chess
        """

    columns = ["Column 1 text. This should def wrap around to line2 correct?",
               "Column 2 text\nAnother line\nAnother line but this one is going to wrap around to lines 3, 4, 5, 6, 7, 8, and 9 or maybe more or less depending on your terminal cols width most definitely!",
               structured_text, "Column 4\n\n\n\n\n\n\n\n\n\n\n\n\nThis is going to jump down a couple lines!", " "]
    total_width = builder.get_available_width()
    print(f'total width: {total_width}')
    widths = total_width // 5
    print(f'widths: {widths}')
    diff = total_width - (widths * 5)
    print(f'diff: {diff}')
    last_width = widths + diff
    print(f'last width: {last_width}')
    print(f'combined_widths: {widths + widths + widths + widths + last_width}')
    col_widths = [widths, widths, widths, widths, last_width]
    col_styles = ['red', 'green', 'yellow', 'blue', 'orange']
    col_alignments = ['left', 'left', 'left', 'center', 'right']

    print(f'\n\n')
    print(f'print_multi_column_box:')
    builder.print_multi_column_box(columns, col_widths, col_styles, col_alignments, double_space_content=True)
    print('\n')
    print(f'print_multi_column_box2:')
    builder.print_multi_column_box2(columns, col_widths, col_styles, col_alignments, col_sep='|')
    print('\n')
    print(f'print_multi_column_box22:')
    builder.print_multi_column_box22(columns, col_widths, col_styles, col_alignments, col_sep='|')
    print('\n')
    print(f'print_multi_column_box2B:')
    builder.print_multi_column_box2B(columns, col_widths, col_styles, col_alignments, col_sep='||', col_sep_style='col_sep', vert_col_alignments='center')
    print('\n')
    print(f'print_multi_column_box2C:')
    builder.print_multi_column_box2C(columns, col_widths, col_styles, col_alignments, col_sep='|', col_sep_style='col_sep', vert_col_alignments='center')
    print('\n')
    print(f'print_multi_column_box3:')
    builder.print_multi_column_box3(columns, col_widths, col_styles, col_alignments)
    print('\n')
    print(f'print_multi_column_box_unified:')
    builder.print_multi_column_box_unified(
        columns=columns,
        col_widths=col_widths,
        col_styles=col_styles,
        col_alignments=col_alignments,
        horiz_border_top=True,
        horiz_border_bottom=True,
        vert_border_left=True,
        vert_border_right=True,
        col_sep=None,  # No custom separator, behave like Method 1
        col_sep_width=1,  # Not relevant here as col_sep=None
        col_widths_percent=False  # No
    )
    print('\n')

    columns = [structured_text]
    col_widths = [builder.get_available_width()]
    col_styles = ['red']
    col_alignments = ['left']
    print(f'print_multi_column_box2:')
    builder.print_multi_column_box2(columns, col_widths, col_styles, col_alignments, col_sep='|')
    print('\n')

    print(f'print_multi_column_box_unified:')
    builder.print_multi_column_box_unified(
        columns=columns,
        col_widths=col_widths,
        col_styles=col_styles,
        col_alignments=col_alignments,
        horiz_border_top=True,
        horiz_border_bottom=True,
        vert_border_left=True,
        vert_border_right=True,
        col_sep='|',  # custom separator like in Method 2
        col_sep_width=1,
        col_widths_percent=False  # Method 2 also supports percentage; if needed, set True and widths as percentages
    )

    print('\n')

    columns = ["Column 1 text\nLine 2. This should def be line2", "Column 2 text\nAnother line", structured_text, "Column 4", " "]
    col_widths = ['', 25, 68, 20, 20]
    col_styles = ['red', 'green', 'blue', 'yellow', 'magenta']
    col_alignments = ['left', 'center', 'left', 'center', 'center']
    print(f'print_multi_column_box2:')
    builder.print_multi_column_box2(columns, col_widths, col_styles, col_alignments, col_sep='|')
    print('\n')

    print(f'print_multi_column_box_unfied:')
    builder.print_multi_column_box_unified(
        columns=columns,
        col_widths=col_widths,
        col_styles=col_styles,
        col_alignments=col_alignments,
        horiz_border_top=True,
        horiz_border_bottom=True,
        vert_border_left=True,
        vert_border_right=True,
        col_sep='|',  # custom separator like in Method 2
        col_sep_width=1,
        col_widths_percent=False  # Method 2 also supports percentage; if needed, set True and widths as percentages
    )

    print('\n')

    columns = ["Column 1 text. This should def wrap around to line2 correct?", "Column 2 text\nAnother line\nAnother line but this one is going to wrap around to lines 3, 4, 5, 6, 7, 8, and 9 or maybe more or less depending on your terminal cols width most definitely!", structured_text, "Column 4\n\n\n\n\n\n\n\n\n\n\n\n\nThis is going to jump down a couple lines!", " "]
    col_widths = ['', 25, 68, 20, 20]
    col_styles = ['red', 'green', 'blue', 'yellow', 'magenta']
    col_alignments = ['left', 'center', 'left', 'center', 'center']
    print(f'print_multi_column_box2:')
    builder.print_multi_column_box2(columns, col_widths, col_styles, col_alignments, col_sep='|')
    print('\n')

    print(f'print_multi_column_box_unified:')
    builder.print_multi_column_box_unified(
        columns=columns,
        col_widths=col_widths,
        col_styles=col_styles,
        col_alignments=col_alignments,
        horiz_border_top=True,
        horiz_border_bottom=True,
        vert_border_left=True,
        vert_border_right=True,
        col_sep='|',  # custom separator like in Method 2
        col_sep_width=1,
        col_widths_percent=False  # Method 2 also supports percentage; if needed, set True and widths as percentages
    )

    print('\n')

    columns = ["Column 1 text\nLine 2. This should def be line2", "Column 2 text\nAnother line"]
    col_widths = ['', 25]
    col_styles = ['red', 'green']
    col_alignments = ['center', 'center']
    print(f'print_multi_column_box2:')
    builder.print_multi_column_box2(columns, col_widths, col_styles, col_alignments, col_sep='|')
    print(pc.apply_style('orange', solid_horiz_rule) * 4)

    print(f'print_multi_column_box_unified:')
    builder.print_multi_column_box_unified(
        columns=columns,
        col_widths=col_widths,
        col_styles=col_styles,
        col_alignments=col_alignments,
        horiz_border_top=True,
        horiz_border_bottom=True,
        vert_border_left=True,
        vert_border_right=True,
        col_sep='|',  # custom separator like in Method 2
        col_sep_width=1,
        col_widths_percent=False  # Method 2 also supports percentage; if needed, set True and widths as percentages
    )
    print(pc.apply_style('orange', solid_horiz_rule) * 4)

    print('\n')

    columns = [structured_text]
    col_widths = [100]
    col_styles = ['red']
    col_alignments = ['left']
    print(f'print_multi_column_box3:')
    builder.print_multi_column_box3(columns, col_widths, col_styles, col_alignments, col_sep='|', col_widths_percent=True)
    print(pc.apply_style('orange', solid_horiz_rule) * 3)
    print('\n')

    print(f'print_multi_column_box_unified:')
    builder.print_multi_column_box_unified(
        columns=columns,
        col_widths=col_widths,
        col_styles=col_styles,
        col_alignments=col_alignments,
        horiz_border_top=True,
        horiz_border_bottom=True,
        vert_border_left=True,
        vert_border_right=True,
        col_sep='|',  # as in Method 3
        col_sep_width=1,
        col_widths_percent=True  # Demonstrating percentage handling just like Method 3
    )

    print(pc.apply_style('orange', solid_horiz_rule) * 3)
    print('\n')

    columns = ["Column 1 text\nLine 2. This should def be line2", "Column 2 text\nAnother line", structured_text, "Column 4", "Col 5"]
    col_widths = ['', 15, 55, 10, 10]
    col_styles = ['red', 'green', 'blue', 'yellow', 'magenta']
    col_alignments = ['left', 'center', 'left', 'center', 'center']
    print(f'print_multi_column_box3:')
    builder.print_multi_column_box3(columns, col_widths, col_styles, col_alignments, col_sep='|', col_widths_percent=True)
    print(pc.apply_style('orange', solid_horiz_rule) * 2)
    print('\n')

    print(f'print_multi_column_box_unified:')
    builder.print_multi_column_box_unified(
        columns=columns,
        col_widths=col_widths,
        col_styles=col_styles,
        col_alignments=col_alignments,
        horiz_border_top=True,
        horiz_border_bottom=True,
        vert_border_left=True,
        vert_border_right=True,
        col_sep='|',  # as in Method 3
        col_sep_width=1,
        col_widths_percent=True  # Demonstrating percentage handling just like Method 3
    )

    print(pc.apply_style('orange', solid_horiz_rule) * 3)
    print('\n')


    columns = ["Column 1 text\nLine 2. This should def be line2", "Column 2 text\nAnother line"]
    col_widths = ['', 25]
    col_styles = ['red', 'green']
    col_alignments = ['center', 'center']
    print(f'print_multi_column_box3:')
    builder.print_multi_column_box3(columns, col_widths, col_styles, col_alignments, col_sep='|', col_widths_percent=True)
    print(pc.apply_style('orange', solid_horiz_rule))

    print('\n')

    print(f'print_multi_column_box_unified:')
    builder.print_multi_column_box_unified(
        columns=columns,
        col_widths=col_widths,
        col_styles=col_styles,
        col_alignments=col_alignments,
        horiz_border_top=True,
        horiz_border_bottom=True,
        vert_border_left=True,
        vert_border_right=True,
        col_sep='|',  # as in Method 3
        col_sep_width=1,
        col_widths_percent=True  # Demonstrating percentage handling just like Method 3
    )

    print(pc.apply_style('orange', solid_horiz_rule) * 3)
    print('\n')

    columns = ["Column 1 text\nLine 2. This should def be line2", "Column 2 text\nAnother line"]
    col_widths = ['', 25]
    col_styles = ['red', 'green']
    col_alignments = ['center', 'center']
    print(f'print_multi_column_box4:')
    builder.print_multi_column_box4(columns, col_widths, col_styles, col_alignments, col_sep='||', col_sep_width=1)
    print()

    print(f'print_multi_column_box_unified:')
    builder.print_multi_column_box_unified(
        columns=columns,
        col_widths=col_widths,  # let one column auto-size
        col_styles=col_styles,
        col_alignments=col_alignments,
        horiz_border_top=True,
        horiz_border_bottom=True,
        vert_border_left=True,
        vert_border_right=True,
        col_sep='||',  # separator character
        col_sep_width=1,  # repeat it thrice, like "|||"
        col_widths_percent=False  # Method 4 does not use percentages
    )
    print('\n')




def divide_container_width(container_width, divisor):
    return container_width // divisor


def main():
    pc = PrintsCharming(styled_strings=styled_strings)
    builder = FrameBuilder(pc=pc, horiz_char='|', vert_width=2, vert_padding=1, vert_char='|', inner_width=2, inner_padding=1, inner_char='|')
    tm = TableManager()
    more_stuff(pc, builder, tm)
    border_boxed_text2(pc, builder, tm)
    nested_boxes_test(pc, builder)






if __name__ == "__main__":
    main()
