from prints_charming import PrintsCharming, PStyle

"""
I got off track and started experimenting with making buttons and showcasing 
more advanced nested functionality within the print2 method, but have made 
some major updates to the PrintsCharming class that i want to push to github 
so this is going with it. Note the print2 method will soon be replacing the 
print method once i merge all current functionality from print into print2.
"""


def experimenting_with_buttons(pc, name):
    pc.print2(f"=== Experimenting With Buttons and Boxed Text Demo ===", f"{name} ===\n", start='\n', end='', color=['orange', 'purple'], italic=True, bold=[False, True], style_args_as_one=False)

    horiz_rule = "==="
    length_horiz_rule = len(horiz_rule)

    box_left = "▎"
    box_right = "▕"
    box1_title = "Simple Divider Demo"
    box1_length = len(box_left + box1_title + box_right)
    top_line_args = [' ' * length_horiz_rule, '▁' * box1_length]
    middle_line_args = [f"{horiz_rule} {box_left}", box1_title, f"{box_right} {horiz_rule} ", f"{name} ==="]
    bottom_line_args = [' ' * length_horiz_rule, '▔' * box1_length]
    pc.print2(*top_line_args, start='\n', color=['default', 'purple'], bold=True, underline=[False, True], style_args_as_one=False)
    pc.print2(*middle_line_args, sep='', color=['purple', 'orange', 'purple', 'purple'], bg_color=['dgray', 'dgray', 'dgray', 'orange'], bold=[False, False, False, True], style_args_as_one=False)
    pc.print2(*bottom_line_args, color=['default', 'purple'], overline=[False, True], style_args_as_one=False)


    top_line_args = [' ' * length_horiz_rule + ' ', '▁' * box1_length]
    bottom_line_args = [' ' * length_horiz_rule + ' ', '▔' * box1_length]

    top_line_args[-1] += '\n'
    middle_line_args[-1] += '\n'


    pc.print2(*top_line_args,
              *middle_line_args,
              *bottom_line_args,
              start='\n',
              sep='',
              color=['default', 'purple', 'purple', 'orange', 'purple', 'purple', 'default', 'purple'],
              bg_color=[None, None, 'dgray', 'dgray', 'dgray', 'orange', None, None],
              bold=[True, True, False, False, False, False, False, False],
              style_args_as_one=False,
              )

    horiz_rule = "=== "
    length_horiz_rule = len(horiz_rule)

    box_left = "▎"
    box_right = "▕"
    box1_title = "Simple Divider Demo"
    box1_length = len(box_left + box1_title + box_right)

    top_line_args_base = [' ' * length_horiz_rule, '▁' * box1_length]
    middle_line_args_base = [f"{horiz_rule}{box_left}", f"{box1_title}", f"{box_right} {horiz_rule}", f"{name} ==="]
    bottom_line_args_base = [' ' * length_horiz_rule, '▔' * box1_length]



    pc.print2(*top_line_args_base, sep='', color=['default', 'purple'], bold=True, underline=[False, True], style_args_as_one=False)
    pc.print2(*middle_line_args_base, sep='', color=['purple', 'orange', 'purple', 'purple'], bg_color=['dgray', 'dgray', 'dgray', 'orange'], bold=[False, False, False, True], style_args_as_one=False)
    pc.print2(*bottom_line_args_base, sep='', color=['default', 'purple'], overline=[False, True], style_args_as_one=False)



    # Create copies of the base arguments
    top_line_args = top_line_args_base.copy()
    middle_line_args = middle_line_args_base.copy()
    bottom_line_args = bottom_line_args_base.copy()

    # Modify the copies for the combined print2 statement
    top_line_args[-1] += '\n'
    middle_line_args[-1] += '\n'
    bottom_line_args[-1] += '\n'

    # Now use the modified arguments in the combined print2 statement
    pc.print2(*top_line_args,
              *middle_line_args,
              *bottom_line_args,
              sep='',
              color=['default', 'purple', 'purple', 'orange', 'purple', 'purple', 'default', 'purple'],
              bg_color=[None, None, 'dgray', 'dgray', 'dgray', 'orange', None, None],
              bold=[True, True, False, False, False, False, False, False],
              style_args_as_one=False)

    #box_left = "▎"
    box_left = "▏"
    box_right = "▕"
    box1_title = "Simple Divider Demo"
    box1_length = len(box_left + box1_title + box_right)

    top_line = '▁' * box1_length
    middle_line = [f"{box_left}", f"{box1_title}", f"{box_right}"]
    bottom_line = '▔' * box1_length

    pc.print2(top_line, color='vcyan', bold=True)
    pc.print2(*middle_line, sep='', color=['vcyan', 'orange', 'vcyan'], bg_color='dgray', style_args_as_one=False)
    pc.print2(bottom_line, color='vcyan', bold=True)

    print()

    top_line += '\n'
    middle_line[-1] += '\n'
    bottom_line += '\n'
    pc.print2(top_line, *middle_line, bottom_line, sep='', color=['purple', 'purple', 'orange', 'purple', 'purple'], bg_color=[None, 'dgray', 'dgray', 'dgray', None], bold=[True, False, False, False, False], style_args_as_one=False)


def divider_selected(pc, name):
    pc.print2('   ', '▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁', start='\n', color=['default', 'purple'], bold=True, underline=[False, True], style_args_as_one=False)

    pc.print2(f"=== ▎Simple Divider Demo▕ ===", f"{name} ===", color=['orange', 'purple'], bg_color=['dgray', 'orange'], overline=False, bold=[False, True], style_args_as_one=False)

    pc.print2('   ', '▔' * 21, color=['default', 'purple'], overline=[False, False], style_args_as_one=False)


def divider_unselected(pc, name):
    pc.print2('   ', '                     ', start='\n', color=['default', 'purple'], bold=True, underline=[False, True], style_args_as_one=False)

    pc.print2(f"=== ▎Simple Divider Demo▕ ===", f"{name} ===", color=['orange', 'purple'], bg_color=['dgray', 'orange'], overline=False, bold=[False, True], style_args_as_one=False)

    pc.print2('   ', '                     ', color=['default', 'purple'], overline=[False, True], style_args_as_one=False)


def divider_unselected2(pc, name):

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


    text = "Apple|Banana|Orange"


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


    text = f'This is a sentence where the way we determine 1 how and 2 where the text gets styled depends on: where the word: that is the dictionary key falls within this text.'

    splits = dict(green='sentence', red='2', orange='gets', blue='word:', yellow='')
    styled_sentence = pc.segment_and_style(text, splits)
    #print(f'{styled_sentence}\n\n')

    pc.print(f'{text}\n\n', style=splits)
    pc.print2(f'{text}\n\n', style=splits)

    styled_sentence2 = pc.segment_and_style_update(text, splits)
    #print(f'{styled_sentence2}\n')


def segment_and_style_example_2(pc, name):

    text = f'This is a sentence where the way we determine 1 how and 2 where the text gets styled depends on: where the word: that is the dictionary key falls within this text.'

    splits = dict(green='sentence', red=['2', 'word:'], blue='gets', yellow='')

    pc.print(f'{text}\n\n', style=splits)
    pc.print2(f'{text}\n\n', style=splits)

    styled_sentence2 = pc.segment_and_style2(text, splits)
    #print(f'{styled_sentence2}\n\n')


def main(pc, name):


    simple_divider_demo(pc, name)
    bordered_box_demo(pc, name)
    gradient_demo(pc, name)
    style_words_by_index(pc, name)
    segment_and_style_example_1(pc, name)
    segment_and_style_example_2(pc, name)


if __name__ == "__main__":
    pc_instances = [PrintsCharming(), PrintsCharming(default_bg_color='jupyter')]
    for i, instance in enumerate(pc_instances, start=1):
        if i == 2:
            break
        instance.trie_manager.add_string("===", 'vcyan')
        main(instance, f'pc{i}')


