import time


from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from prints_charming import (
    PrintsCharming,
    DEFAULT_CONFIG,
    DEFAULT_COLOR_MAP,
    DEFAULT_EFFECT_MAP,
    DEFAULT_STYLES,
    DEFAULT_LOGGING_STYLES
)





class InteractiveMenu:
    def __init__(self, options, pc=None, selected_style=None, unselected_style=None, confirmed_style=None, previous='p', next='n'):
        self.pc = pc or PrintsCharming()
        self.options = options
        self.selected_style = selected_style or 'vcyan'
        self.unselected_style = unselected_style or 'default'
        self.confirmed_style = confirmed_style or 'vgreen'
        self.selected_index = 0
        self.previous = previous  # Custom key for moving to the previous option
        self.next = next  # Custom key for moving to the next option

    def display_highlighted_menu(self):
        for i, option in enumerate(self.options):
            style = self.selected_style if i == self.selected_index else self.unselected_style
            self.pc.print(f"{i + 1}. {option}", style=style)

    def navigate(self, direction):
        self.selected_index = (self.selected_index + direction) % len(self.options)
        print(PrintsCharming.CONTROL_MAP['clear_screen'], PrintsCharming.CONTROL_MAP['cursor_home'])

        self.display_highlighted_menu()

    def run(self):
        print(PrintsCharming.CONTROL_MAP['alt_buffer'])
        print(PrintsCharming.CONTROL_MAP['cursor_home'])  # Move to top-left corner
        # Display instructions
        styled_instructions = self.pc.apply_style(style_name='vgreen', text='Instructions:')
        print(styled_instructions)
        self.pc.print(f"  Use '{self.previous}' to move up, '{self.next}' to move down, and press Enter to select.", style="default")
        self.pc.print(f"  Press 'q' to quit.", style="vred")
        print()

        self.display_highlighted_menu()
        while True:
            key = input()
            if key == 'q':
                break
            elif key == self.previous:
                self.navigate(-1)
            elif key == self.next:
                self.navigate(1)
            elif key == '':
                confirmed_option = self.options[self.selected_index]
                self.pc.print(f"Selected: {self.options[self.selected_index]}", style=self.confirmed_style)
                time.sleep(2)
                break

        print(PrintsCharming.CONTROL_MAP['normal_buffer'])
        self.pc.print(f"Selected: {self.options[self.selected_index]}", style=self.confirmed_style)



"""
class InteractiveMenu:
    def __init__(self, options, pc=None, styles=None, key_bindings=None, state=None, config=None):
        self.styles = styles or {
            'selected': PrintsStyle(color='vcyan'),
            'unselected': PrintsStyle(),
            'confirmed': PrintsStyle(color='vgreen'),
            'multi_selected': PrintsStyle(color='vyellow')
        }
        self.pc = pc or PrintsCharming()
        self.control_map = self.pc.CONTROL_MAP  # Use control map from PrintsCharming instance
        self.options = options

        self.key_bindings = key_bindings or {}
        self.state = state or {
            'selected_index': 0,
            'selected_items': set(),  # For multi-selection
            'search_query': "",
        }
        self.config = config or {
            'multi_select': False,
            'editable': False,
            'searchable': False,
            'hierarchical': False,
            'scrollable': False,
            'confirm_required': False,
        }

    def display_menu(self):
        start_index, end_index = self.get_scroll_indices()
        for i, option in enumerate(self.options[start_index:end_index]):
            global_index = i + start_index
            style = self.determine_style(global_index)
            self.pc.print(f"{global_index + 1}. {option}", style=style)

    def get_scroll_indices(self):
        if not self.config['scrollable']:
            return 0, len(self.options)
        max_display = 10  # Example: Display 10 items at a time
        start_index = max(0, self.state['selected_index'] - max_display // 2)
        end_index = min(len(self.options), start_index + max_display)
        return start_index, end_index

    def determine_style(self, global_index):
        if global_index == self.state['selected_index']:
            return self.styles['selected']
        elif global_index in self.state['selected_items']:
            return self.styles['multi_selected']
        else:
            return self.styles['unselected']

    def run(self):
        raise NotImplementedError("Subclasses should implement this method to provide specific behavior.")

"""