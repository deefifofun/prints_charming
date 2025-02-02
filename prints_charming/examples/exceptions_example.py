from prints_charming import PrintsCharming
from prints_charming.exceptions import PrintsCharmingException


class ColorNotFoundError(PrintsCharmingException):
    pass


def raise_custom_error(pc, color_name='tree_color', length=10):
    bg_color_code = pc.bg_color_map.get(color_name)
    if not bg_color_code:
        message = f"Key '{color_name}' not in 'self.bg_color_map'."
        styled_message = pc.apply_style('vred', message)
        raise ColorNotFoundError(styled_message,
                                 pc,
                                 format_specific_exception=True,)
    bg_bar_strip = f"{bg_color_code}{' ' * length}{pc.reset}"

    return bg_bar_strip



def except_custom_error(pc):
    pc.print(f'This will purposely cause an error that is styled\n\n', color='vgreen')

    try:
        bg_bar_strip = raise_custom_error(pc)
        print(bg_bar_strip)
    except ColorNotFoundError as e:
        e.handle_exception()




def main():
    pc = PrintsCharming()
    except_custom_error(pc)


if __name__ == '__main__':
    main()



