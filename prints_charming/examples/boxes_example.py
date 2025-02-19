from typing import Dict, List, Optional, Tuple, NamedTuple
import inspect
from collections import namedtuple
from prints_charming import PrintsCharming




class Segment(NamedTuple):
    text: str
    style: any


def build_top_line(box_top: str, length: int, style, partial: bool) -> Segment:
    """Constructs the top line segment with its style.
       If partial is True, only the left and right corners are drawn.
    """
    if partial:
        # Default corner characters if not provided.
        top_left_char = box_top[0]
        top_right_char = box_top[0]
        # The top line is a left corner, then spaces, then a right corner.
        text = top_left_char + (" " * (length - 2)) + top_right_char
    else:
        # Full top line: repeat the character.
        text = box_top * length
    return Segment(text, style)


def build_bottom_line(box_bottom: str, length: int, style, partial: bool) -> Segment:
    """Constructs the bottom line segment with its style.
       If partial is True, only the left and right corners are drawn.
    """
    if partial:
        bottom_left_char = box_bottom[0]
        bottom_right_char = box_bottom[0]
        text = bottom_left_char + (" " * (length - 2)) + bottom_right_char
    else:
        text = box_bottom * length
    return Segment(text, style)


def build_middle_line(box_left: str, content: str, box_right: str,
                       left_style, center_style, right_style) -> list[Segment]:
    """Constructs the three segments for the middle line with their styles."""
    left = Segment(box_left, left_style)
    center = Segment(content, center_style)
    right = Segment(box_right, right_style)
    return [left, center, right]


def print_box(
        content,
        box_top: str = '▁',
        box_left: str = '▎',
        box_right: str = '▕',
        box_bottom: str = '▔',
        space_char: str = ' ',
        width: int = None,  # Optional overall width.
        h_align: str = 'center',  # 'left', 'center', or 'right'.
        size: str = 'small',
        v_align: str = 'center',
        partial_box: bool = False,  # New: when True, draw only corner characters on top/bottom.

        # Style parameters for each segment.
        default_style: bool = True,
        selected: bool = False,
        top_style=None,
        mid_left_style=None,
        mid_content_style=None,
        mid_right_style=None,
        bottom_style=None,
        newline_style='default'
):
    """
    Prints a box around the given text in a single pc.print2 call.

    In full-box mode, the top and bottom lines are drawn as continuous lines.
    In partial (or bracketed) mode, the top and bottom lines consist only of a
    left corner and a right corner (with space in between) so that the box appears
    as a giant bracket surrounding the content.
    """
    # Use default style names if requested.
    if default_style:
        state = '_selected' if selected else '_unselected'
        if partial_box:
            state += '_partial'
        top_style = f'box_top{state}'
        mid_left_style = f'box_left{state}'
        mid_content_style = f'box_content{state}'
        mid_right_style = f'box_right{state}'
        bottom_style = f'box_bottom{state}'



    # Evaluate content if callable.
    if callable(content):
        content = content()

    # Compute minimum width needed (based on the middle line).
    min_width = len(box_left + content + box_right)
    width = width if width is not None else min_width
    width = max(width, min_width)

    # Calculate extra padding for the middle line based on horizontal alignment.
    extra_spaces = width - min_width
    if h_align == 'left':
        left_spaces = 0
        right_spaces = extra_spaces
    elif h_align == 'right':
        left_spaces = extra_spaces
        right_spaces = 0
    else:  # center
        left_spaces = extra_spaces // 2
        right_spaces = extra_spaces - left_spaces

    # Build the top and bottom segments.
    top_seg = build_top_line(box_top, width, top_style, partial_box)
    bottom_seg = build_bottom_line(box_bottom, width, bottom_style, partial_box)

    # For the middle line, include padding on the left and right sides.
    mod_left = box_left + (space_char * left_spaces)
    mod_right = (space_char * right_spaces) + box_right

    # Determine how many lines in the middle (1 or 3).
    # For 'large', pick which of the 3 lines contains the content.
    if size == 'small':
        lines = [content]  # only one line
    elif size == 'large':
        if v_align == 'top':
            lines = [content, '', '']
        elif v_align == 'bottom':
            lines = ['', '', content]
        else:  # center
            lines = ['', content, '']
    else:
        raise ValueError("size must be either 'small' or 'large'")

    # Figure out how wide the center segment must be
    # so the entire line sums up to 'width'.
    # total length = len(mod_left) + len(center) + len(mod_right) == width
    left_len = len(mod_left)
    right_len = len(mod_right)
    center_width = width - (left_len + right_len)

    # Build each middle line, padding empty lines to match center_width.
    # This ensures every line is exactly 'width' in total length.
    middle_segments = []
    for i, line in enumerate(lines):
        # If the line is shorter than center_width, pad it with spaces so the
        # total line length remains consistent.
        if len(line) < center_width:
            # Left-align the text in the center segment, but you could do your own alignment here
            line = line + (' ' * (center_width - len(line)))

        # Build the line using build_middle_line.
        mid_line = build_middle_line(mod_left, line, mod_right,
                                     mid_left_style, mid_content_style, mid_right_style)
        # Add the segments for this line to our list.
        middle_segments.extend(mid_line)

        # Add a newline segment unless it's the last middle line.
        if i < len(lines) - 1:
            middle_segments.append(Segment("\n", newline_style))

    # Finally assemble all segments.
    newline_seg = Segment("\n", newline_style)
    final_segments = [top_seg, newline_seg] + middle_segments + [newline_seg, bottom_seg]

    # Extract the text and style in parallel lists.
    contents_list = [seg.text for seg in final_segments]
    styles_list = [seg.style for seg in final_segments]

    # Single print call.
    pc.print2(*contents_list, style=styles_list, sep='', style_args_as_one=False)




def main():
    # Full box (default)
    print_box("Full Box Example", width=25)
    print("\n")
    # Partial (bracketed) box – top and bottom are just corners.
    print_box("Partial Box Example", width=30, partial_box=True)
    print()
    # Partial (bracketed) box – top and bottom are just corners.
    print_box("Partial Box Example", width=30, partial_box=True)
    print()
    # Ensure pc is your PrintsCharming instance.
    print("Small box (default):")
    print_box("Box Content", width=30)
    print("\nLarge box with centered content:")
    print_box("Box Content", width=30, size='large', v_align='center')
    print("\nLarge box with top-aligned content:")
    print_box("Box Content", width=30, size='large', v_align='top')
    print("\nLarge box with bottom-aligned content:")
    print_box("Box Content", width=30, size='large', v_align='bottom')
    print()





if __name__ == '__main__':
    pc = PrintsCharming()
    main()