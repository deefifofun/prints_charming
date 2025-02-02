import inspect
from functools import partial
from typing import Optional
from prints_charming import PrintsCharming, PStyle




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


def print_box1(pc, name, text, horiz_rule='===', box_top='▁', box_left="▎", box_right="▕", box_bottom='▔', space_char=' '):
    pc.print2(f"{get_pretty_caller_function_name()}", start='\n', end='\n', color='orange', italic=True, bold=True, fill_to_end=True if pc.default_bg_color else None)

    pc.print2(f"{get_pretty_caller_function_name()}", start='\n', end='\n', color='orange')

    pc.print(f"{get_pretty_caller_function_name()}", start='\n', end='\n', style='orange')


    pc.print2(f"{get_pretty_caller_function_name()}", f"{name} ===\n", start='\n', end='', color=['orange', 'purple'], italic=True, bold=True, style_args_as_one=False)



    if callable(text):
        text = text()

    horiz_rule_length = len(horiz_rule)
    box_length = len(box_left + text + box_right)

    # Top
    top_line_args = [space_char * horiz_rule_length, box_top * box_length]
    top_color = ['default', 'purple']
    top_bold = True
    top_underline = [False, True]
    pc.print2(*top_line_args, start='\n', color=top_color, bold=top_bold, underline=top_underline, style_args_as_one=False)

    # Middle
    middle_line_args = [f"{horiz_rule} {box_left}", text, f"{box_right} {horiz_rule} ", f"{name} ==="]
    middle_sep = ''
    middle_color = ['purple', 'orange', 'purple', 'purple']
    middle_bg_color = ['dgray', 'dgray', 'dgray', 'orange']
    middle_bold = [False, False, False, True]
    pc.print2(*middle_line_args, sep=middle_sep, color=middle_color, bg_color=middle_bg_color, bold=middle_bold, style_args_as_one=False)

    # Bottom
    bottom_line_args = [space_char * horiz_rule_length, box_bottom * box_length]
    bottom_color = ['default', 'purple']
    bottom_overline = [False, True]
    pc.print2(*bottom_line_args, color=bottom_color, overline=bottom_overline, style_args_as_one=False)


def print_box2(pc, name, text,
               horiz_rule='===',
               box_top='▁',
               box_left="▎",
               box_right="▕",
               box_bottom='▔',
               space_char=' '):
    pc.print2(f"{get_pretty_caller_function_name()}", start='\n', end='\n', color=['orange', 'purple'], italic=True, bold=[False, True], fill_to_end=True, style_args_as_one=False)

    if callable(text):
        text = text()

    horiz_rule_length = len(horiz_rule)
    box_length = len(box_left + text + box_right)

    top_line_args = [space_char * horiz_rule_length + space_char, box_top * box_length + '\n']
    middle_line_args = [f"{horiz_rule} {box_left}", text, f"{box_right} {horiz_rule} ", f"{name} ===\n"]
    bottom_line_args = [space_char * horiz_rule_length + space_char, box_bottom * box_length]

    #top_line_args[-1] += '\n'
    #middle_line_args[-1] += '\n'

    box_colors = ['default', 'purple', 'purple', 'orange', 'purple', 'purple', 'default', 'purple']
    box_bg_colors = [None, None, 'dgray', 'dgray', 'dgray', 'orange', None, None]
    box_bolds = [True, True, False, False, False, False, False, False]

    # Box2
    pc.print2(*top_line_args, *middle_line_args, *bottom_line_args, start='\n', sep='', color=box_colors, bg_color=box_bg_colors, bold=box_bolds, style_args_as_one=False)



def print_box3_and_box4(pc, name, text, horiz_rule='===', box_top='▁', box_left="▎", box_right="▕", box_bottom='▔', space_char=' '):
    pc.print2(f"{get_pretty_caller_function_name()}", start='\n', end='\n', color=['orange', 'purple'], italic=True, bold=[False, True], style_args_as_one=False)

    # Box3
    text1 = text[0]
    if callable(text1):
        text1 = text1()


    horiz_rule_length = len(horiz_rule)
    box1_length = len(box_left + text1 + box_right)

    # Top
    top_line_args_base = [space_char * horiz_rule_length, box_top * box1_length]
    top_base_color = ['default', 'purple']
    top_base_bold = True
    top_base_underline = [False, True]
    pc.print2(*top_line_args_base, color=top_base_color, bold=top_base_bold, underline=top_base_underline, style_args_as_one=False)

    # Middle
    middle_line_args_base = [f"{horiz_rule} {box_left}", f"{text1}", f"{box_right} {horiz_rule} ", f"{name} ==="]
    middle_base_color = ['purple', 'orange', 'purple', 'purple']
    middle_base_bg_color = ['dgray', 'dgray', 'dgray', 'orange']
    middle_base_bold = [False, False, False, True]
    pc.print2(*middle_line_args_base, sep='', color=middle_base_color, bg_color=middle_base_bg_color, bold=middle_base_bold, style_args_as_one=False)

    # Bottom
    bottom_line_args_base = [space_char * horiz_rule_length, box_bottom * box1_length]
    bottom_base_color = ['default', 'purple']
    bottom_base_overline = [False, True]
    pc.print2(*bottom_line_args_base, color=bottom_base_color, overline=bottom_base_overline, style_args_as_one=False)



    # Box4
    text2 = text[1]
    if callable(text2):
        text2 = text2()

    box2_length = len(box_left + text2 + box_right)


    # Create copies of the base arguments
    top_line_args = top_line_args_base.copy()
    middle_line_args = middle_line_args_base.copy()
    bottom_line_args = bottom_line_args_base.copy()

    # Modify the copies for the combined print2 statement
    top_line_args[0] += space_char
    top_line_args[-1] = box_top * box2_length
    top_line_args[-1] += '\n'

    middle_line_args[1] = text2
    middle_line_args[-1] += '\n'

    bottom_line_args[0] += space_char
    bottom_line_args[-1] = box_bottom * box2_length
    bottom_line_args[-1] += '\n'

    colors = ['default', 'purple', 'purple', 'orange', 'purple', 'purple', 'default', 'purple']
    bg_colors = [None, None, 'dgray', 'dgray', 'dgray', 'orange', None, None]
    bolds = [True, True, False, False, False, False, False, False]

    # Now use the modified arguments in the combined print2 statement
    pc.print2(*top_line_args,
              *middle_line_args,
              *bottom_line_args,
              sep='',
              color=colors,
              bg_color=bg_colors,
              bold=bolds,
              style_args_as_one=False)


def print_box5_and_box6(pc, text, box_top='▁', box_left="▏", box_right="▕", box_bottom='▔', space_char=' ', cols=6, col_idx=1, align='left'):

    pc.print2(f"{get_pretty_caller_function_name()}", start='\n', end='\n', color=['orange', 'purple'], italic=True, bold=[False, True], style_args_as_one=False)

    # Box5
    text1 = text[0]
    if callable(text1):
        text1 = text1()

    box1_length = len(box_left + text1 + box_right)

    # Top
    top_line = box_top * box1_length
    top1_color = 'vcyan'
    top1_bold = True
    pc.print2(top_line, color=top1_color, bold=top1_bold)

    # Middle
    middle_line = [f"{box_left}", f"{text1}", f"{box_right}"]
    middle1_color = ['vcyan', 'orange', 'vcyan']
    middle1_bg_color = 'dgray'
    pc.print2(*middle_line, sep='', color=middle1_color, bg_color=middle1_bg_color, style_args_as_one=False)

    # Bottoms
    bottom_line = box_bottom * box1_length
    bottom1_color = 'vcyan'
    bottom1_bold = True
    pc.print2(bottom_line, color=bottom1_color, bold=bottom1_bold)


    # Box6
    text2 = text[1]
    if callable(text2):
        text2 = text2()

    box2_length = len(box_left + text2 + box_right)


    top_line = box_top * box2_length + '\n'

    #middle_line_args[1] = f'{text2}'
    #middle_line_args[-1] += '\n'
    middle_line_args = [f"{box_left}", f"{text1}", f"{box_right}", '\n']

    bottom_line = box_bottom * box2_length + '\n'

    colors = ['purple', 'purple', 'orange', 'purple', None, 'purple']
    bg_colors = [None, 'dgray', 'dgray', 'dgray', None, None]
    bolds = [True, True, False, True, False, True]

    pc.print2(top_line, *middle_line_args, bottom_line, sep='', color=colors, bg_color=bg_colors, bold=bolds, style_args_as_one=False)




def experimenting_with_buttons(pc, name):
    pc.print2(f"{get_pretty_caller_function_name()}", f"{name} ===\n", start='\n', end='', color=['lav', 'purple'], italic=True, bold=[False, True], style_args_as_one=False)

    print_box1(pc, name, "This is Box1")
    print_box2(pc, name, "This is Box2")
    print_box3_and_box4(pc, name, ["This is Box3", "This is Box4"])
    print_box5_and_box6(pc, ["This is Box5", "This is Box6"])




def create_boxed_text(text, top="▁", left="▏", right="▕", bottom="▔", size='small'):
    if callable(text):
        text = text()

    box_len = len(left + text + right)

    if size == 'small':
        line1 = top * box_len + '\n'
        line2 = [f"{left}", f"{text}", f"{right}", "\n"]
        line3 = bottom * box_len + '\n'
        lines1 = [line1, *line2, line3]
        return lines1
    else:
        line1 = top * box_len + '\n' + left + (len(text) * ' ') + right + '\n'
        line2 = f"{left}{text}{right}\n{left}{len(text) * ' '}{right}\n"
        line3 = bottom * box_len + '\n'
        #lines2 = [line1, *line2, line3]
        lines2 = [line1, line2, line3]
        return lines2



def print_text(pc, text, **kwargs):
    pc.printnl(bg_color='yellow')
    pc.print2(" ", f"{get_pretty_caller_function_name()}", " ", sep='', start='\t', end='\n', color=[None, 'orange', 'purple'], bg_color=['green', None, 'green'], italic=True, bold=[False, True, True], style_args_as_one=False, prepend_fill=True, fill_to_end=True)
    pc.printnl()
    pc.print2(" ", f"{get_pretty_caller_function_name()}", " ", sep='', start='\t', end='\n', color=[None, 'orange', 'purple'], bg_color=['green', None, 'green'], italic=True, bold=[False, True, True], style_args_as_one=False, prepend_fill=True, fill_to_end=True)
    pc.printnl(bg_color='yellow')
    pc.print2(" ", f"{get_pretty_caller_function_name()}", " ", sep='', start='\t', end='\n', color=[None, 'orange', 'purple'], bg_color=['green', None, 'green'], italic=True, bold=[False, True, True], style_args_as_one=False, prepend_fill=True, fill_to_end=True)
    pc.printnl()
    pc.print2(" ", f"{get_pretty_caller_function_name()}", " ", sep='', start='\t', end='\n', color=[None, 'orange', 'purple'], bg_color=['green', None, 'green'], italic=True, bold=[False, True, True], style_args_as_one=False, prepend_fill=True, fill_to_end=True)
    pc.printnl(bg_color='yellow')
    pc.print2(" ", f"{get_pretty_caller_function_name()}", " ", sep='', start='\t', end='\n', color=[None, 'orange', 'purple'], bg_color=['green', None, 'green'], italic=True, bold=[False, True, True], style_args_as_one=False, prepend_fill=True, fill_to_end=True)
    pc.printnl()
    pc.print2(" ", f"{get_pretty_caller_function_name()}", " ", sep='', start='\t', end='\n', color=[None, 'orange', 'purple'], bg_color=['green', None, 'green'], italic=True, bold=[False, True, True], style_args_as_one=False, prepend_fill=True, fill_to_end=True)
    pc.printnl(bg_color='yellow')
    pc.print2(" ", f"{get_pretty_caller_function_name()}", " ", sep='', start='\t', end='\n', color=[None, 'orange', 'purple'], bg_color=['green', None, 'green'], italic=True, bold=[False, True, True], style_args_as_one=False, prepend_fill=True, fill_to_end=True)
    pc.printnl()
    pc.print2(" ", f"{get_pretty_caller_function_name()}", " ", sep='', start='\t', end='\n', color=[None, 'orange', 'purple'], bg_color=['green', None, 'green'], italic=True, bold=[False, True, True], style_args_as_one=False, prepend_fill=True, fill_to_end=True)
    pc.printnl(bg_color='yellow')


    for newline in range(3):
        pc.printnl()
    is_list = False
    if isinstance(text, list):
        is_list = True

    pc.print2(*text if is_list else text, **kwargs)


def print_boxed_text(pc, sep=''):
    boxed_text_lines = create_boxed_text(get_pretty_caller_function_name)
    style = ['purple', 'purple', 'orange', 'purple', None, 'purple']
    bg_color = ['yellow', 'dgray', 'dgray', 'dgray', 'blue', 'green']
    bold = [True, False, False, False, False, False]
    fill_to_end = [True, False, False, False, True, False]
    style_args_as_one = False

    print_text(pc, boxed_text_lines, sep=sep, style=style, bg_color=bg_color, bold=bold, fill_to_end=fill_to_end,
               style_args_as_one=style_args_as_one)

    boxed_text_lines = create_boxed_text(get_pretty_caller_function_name, size='large')
    color = ['purple', 'purple', 'orange', 'purple', 'purple']
    bg_color = [None, 'dgray', 'dgray', 'dgray', None]
    bold = [True, False, False, False, False]
    style_args_as_one = False

    print_text(pc, boxed_text_lines, sep=sep, color=color, bg_color=bg_color, bold=bold,
               style_args_as_one=style_args_as_one)




def divider_selected(pc, name):
    pc.print2(f"=== Divider Selected ===", f"{name} ===\n", color=['orange', 'purple'], italic=True, bold=[False, True], style_args_as_one=False)

    pc.print2('   ', '▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁', start='\n', color=['default', 'purple'], bold=True, underline=[False, True], style_args_as_one=False)

    pc.print2(f"=== ▎Simple Divider Demo▕ ===", f"{name} ===", color=['orange', 'purple'], bg_color=['dgray', 'orange'], overline=False, bold=[False, True], style_args_as_one=False)

    pc.print2('   ', '▔' * 21, color=['default', 'purple'], overline=[False, False], style_args_as_one=False)


def divider_unselected(pc, name):
    pc.print2(f"=== Divider Unselected ===", f"{name} ===\n", color=['orange', 'purple'], italic=True, bold=[False, True], style_args_as_one=False)

    pc.print2('   ', '                     ', start='\n', color=['default', 'purple'], bold=True, underline=[False, True], style_args_as_one=False)

    pc.print2(f"=== ▎Simple Divider Demo▕ ===", f"{name} ===", color=['orange', 'purple'], bg_color=['dgray', 'orange'], overline=False, bold=[False, True], style_args_as_one=False)

    pc.print2('   ', '                     ', color=['default', 'purple'], overline=[False, True], style_args_as_one=False)


def divider_unselected2(pc, name):
    pc.print2(f"=== Divider Unselected2 ===", f"{name} ===\n", color=['orange', 'purple'], italic=True, bold=[False, True], style_args_as_one=False)

    pc.print2('   ', '                     ', start='\n', color=['default', 'purple'], bold=True, underline=[False, True], style_args_as_one=False)

    pc.print2("=== ▎", "Simple Divider Demo", "▕ === ", f"{name} ===", sep='', color=['purple', 'orange', 'purple', 'purple'], bg_color=['dgray', 'dgray', 'dgray', 'orange'], bold=[False, False, False, True], style_args_as_one=False)

    pc.print2('   ', '                     ', color=['default', 'purple'], overline=[False, True], style_args_as_one=False)



    pc.print2('   ', '▁' * 21, start='\n', color=['default', 'purple'], bold=True, underline=[False, True], style_args_as_one=False)

    pc.print2("=== ▎", "Simple Divider Demo", "▕ === ", f"{name} ===", sep='', color=['purple', 'orange', 'purple', 'purple'], bg_color=['dgray', 'dgray', 'dgray', 'orange'],
              bold=[False, False, False, True], style_args_as_one=False)

    pc.print2('   ', '▔' * 21, color=['default', 'purple'], overline=[False, True], style_args_as_one=False)



    pc.print2(' ' * 3, '▁' * 21, start='\n', color=['default', 'purple'], bold=True, underline=[False, True], style_args_as_one=False)

    pc.print2("=== ▎", "Simple Divider Demo", "▕ === ", f"{name} ===", sep='', color=['purple', 'orange', 'purple', 'purple'], bg_color=['dgray', 'dgray', 'dgray', 'orange'],
              bold=[False, False, False, True], style_args_as_one=False)

    pc.print2('   ', '▔' * 21, end='\n\n', color=['default', 'purple'], overline=[False, True], style_args_as_one=False)



def simple_divider_demo(pc, name):
    experimenting_with_buttons(pc, name)
    divider_selected(pc, name)
    divider_unselected(pc, name)
    divider_unselected2(pc, name)


    text = "|Apple|Banana|Orange|"


    output = pc.segment_with_splitter_and_style(
        text=text,
        splitter_match="|",
        splitter_swap=" | ",
        splitter_show=True,
        splitter_style=["red"],
        splitter_arms=True,
        string_style=["green"]
    )
    print(output, end='\n\n')


def bordered_box_demo(pc, name):
    pc.print2(f"=== Bordered Box Demo ===", f"{name} ===\n", color=['orange', 'purple'], italic=True, bold=[False, True], style_args_as_one=False)
    header = "HEADER"
    content = "Cell1,Cell2,Cell3\nCell4,Cell5,Cell6"
    border_style = ["cyan"]
    segment_style = ["green", "magenta"]

    top_border = (
        f"{pc.style_codes[border_style[0]]}+{'-' * len(header)}+{pc.reset}"
    )

    rows = []
    for line in content.split("\n"):
        styled_row = pc.segment_with_splitter_and_style(
            text="|" + line + "|",
            splitter_match=",",  # Split content into cells
            splitter_swap="|",  # Replace with vertical divider
            splitter_show=True,
            splitter_style=border_style,
            splitter_arms=True,
            string_style=segment_style
        )
        rows.append(styled_row)

    bottom_border = top_border  # Reuse the styled top border

    box = f"{top_border}\n{'\n'.join(rows)}\n{bottom_border}"
    print(box)


def gradient_demo(pc, name):
    pc.print2(f"=== Gradient Effect Demo ===", f"{name} ===\n", color=['orange', 'purple'], italic=True, bold=[False, True], style_args_as_one=False)
    text = "This is a sentence that will showcase a gradient effect."
    styles = ["red", "yellow", "green", "cyan", "blue", "magenta"]
    output = pc.segment_with_splitter_and_style(
        text=text,
        splitter_match=" ",
        splitter_swap=" ",
        splitter_show=True,
        splitter_style=styles,
        splitter_arms=True,
        string_style=styles
    )
    print(output)

    """
    original_styles = {
        name: pc.styles[name] for name in styles if name in pc.styles
    }

    reversed_styles = PStyle.toggle_reverse_batched(original_styles)
    pc.add_styles(reversed_styles)

    reversed_styles = list(reversed_styles)
    #reversed_styles = ['red_reversed', 'yellow_reversed', 'green_reversed', 'cyan_reversed']

    output2 = pc.segment_with_splitter_and_style(
        text=text,
        splitter_match=" ",
        splitter_swap=" ",
        splitter_show=True,
        splitter_style=styles,
        splitter_arms=True,
        string_style=reversed_styles
    )

    print(output2)

    print(output2)
    #print(f'\n{pc.escape_ansi_codes(output3)}')
    """


def style_words_by_index(pc, name):
    pc.print2(f"=== Style Words By Index Demo ===", f"{name} ===\n", start='\n', color=['orange', 'purple'], italic=True, bold=[False, True], style_args_as_one=False)


    indexed_style = {
        1: "vgreen",
        (2, 4): "blue",
        (5, 6): "yellow",
        7: "purple",
        (8, 10): "pink"
    }

    text1 = "These,    words are going to be    styled by their indexes."

    index_styled_text = pc.style_words_by_index(text1, indexed_style)
    print(f'{index_styled_text}\n')  # 1

    pc.print(text1, style=indexed_style, end='\n\n')  # 2

    pc.print2(f"Orange text here,", text1, "more orange text.", style=[None, indexed_style, None, None], color=['orange', None, 'orange'], skip_ansi_check=True, style_args_as_one=False)

    pc.print(f'Orange text here, {index_styled_text} more orange text.', color='orange', skip_ansi_check=True, end='\n\n\n')  # 3

    pc.print2(f'Orange text here, {index_styled_text} more orange text.', color='orange', skip_ansi_check=True, end='\n\n\n')  # 3


    pc.print2(f'Orange text here,', index_styled_text, f'more orange text.', 'gold text here!', color=['orange', None, 'orange', 'gold'], skip_ansi_check=True, style_args_as_one=False, end='\n\n\n')  # 4
    pc.print2(f"Orange text here,", text1, "more orange text.", "gold text here!", style=[None, indexed_style, None, None], color=['orange', None, 'orange', 'gold'], skip_ansi_check=True, style_args_as_one=False, end='\n\n\n\n\n')


def segment_and_style_example_1(pc, name):
    pc.print2(f"=== Segment and Style Example 1 ===", f"{name} ===\n", color=['orange', 'purple'], italic=True, bold=[False, True], style_args_as_one=False)

    text = f'This is a sentence where the way we determine 1 how and 2 where the text gets styled depends on: where the word: that is the dictionary key falls within this text.'

    splits = dict(green='sentence', red='2', orange='gets', blue='word:', yellow='')
    styled_sentence = pc.segment_and_style(text, splits)
    #print(f'{styled_sentence}\n\n')

    pc.print(f'{text}\n\n', style=splits)
    pc.print2(f'{text}\n\n', style=splits)

    styled_sentence2 = pc.segment_and_style_update(text, splits)
    #print(f'{styled_sentence2}\n')


def segment_and_style_example_2(pc, name):
    pc.print2(f"=== Segment and Style Example 2 ===", f"{name} ===\n", color=['orange', 'purple'], italic=True, bold=[False, True], style_args_as_one=False)

    text = f'This is a sentence where the way we determine 1 how and 2 where the text gets styled depends on: where the word: that is the dictionary key falls within this text.'

    splits = dict(green='sentence', red=['2', 'word:'], blue='gets', yellow='')

    pc.print(f'{text}\n\n', style=splits)
    pc.print2(f'{text}\n\n', style=splits)

    styled_sentence2 = pc.segment_and_style2(text, splits)
    #print(f'{styled_sentence2}\n\n')


def main(pc, name):

    print_boxed_text(pc)
    simple_divider_demo(pc, name)
    #bordered_box_demo(pc, name)
    #gradient_demo(pc, name)
    #style_words_by_index(pc, name)
    #segment_and_style_example_1(pc, name)
    #segment_and_style_example_2(pc, name)


if __name__ == "__main__":
    pc_instances = [PrintsCharming(), PrintsCharming(default_bg_color='jupyter')]
    for i, instance in enumerate(pc_instances, start=1):
        #if i == 2:
            #break
        instance.trie_manager.add_string("===", 'vcyan')
        main(instance, f'pc{i}')


