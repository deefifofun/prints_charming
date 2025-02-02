import pytest
from unittest.mock import MagicMock, patch


# We'll define a mock PrintsCharming class to simulate the required methods.
class MockPrintsCharming:
    def __init__(self):
        self.reset = MagicMock()
        self.apply_style = MagicMock(side_effect=lambda style_name, text: f"{style_name}:{text}")
        self.ctl_map = {
            'arrow_up': 'UP',
            'arrow_down': 'DOWN',
            'arrow_left': 'LEFT',
            'arrow_right': 'RIGHT'
        }
        self.unicode_map = {}
        self.write = MagicMock()
        self.print = MagicMock()
        self.warning = MagicMock()

    @classmethod
    def get_shared_instance(cls, key):
        return None  # By default, return None unless we mock differently


# Mock the get_key function
def mock_get_key_sequence(inputs):
    # Returns a generator that yields each input once.
    def _inner():
        for inp in inputs:
            yield inp
    gen = _inner()
    return lambda: next(gen)


# We'll patch PrintsCharming and get_key globally in the tests below
@pytest.fixture
def mock_pc():
    with patch('interactive_menu.PrintsCharming', new=MockPrintsCharming):
        yield


@pytest.fixture
def mock_get_key():
    # We'll parameterize this in tests where needed
    pass


# Now import the class under test after mocking
from prints_charming import InteractiveMenu


def test_shared_instance_methods(mock_pc):
    instance1 = InteractiveMenu()
    InteractiveMenu.set_shared_instance(instance1, "menu_key")
    assert InteractiveMenu.get_shared_instance("menu_key") is instance1
    assert InteractiveMenu.get_shared_instance("non_existent_key") is None


def test_initialization_defaults(mock_pc):
    menu = InteractiveMenu()
    assert menu.unselected_style == 'default'
    assert menu.selected_style is None
    assert menu.confirmed_style is None
    assert menu.current_menu is None


def test_initialization_with_pc_string_no_shared_instance(mock_pc):
    # Passing a string to pc, none shared under that key
    menu = InteractiveMenu(pc="non_existent")
    # Should have created a new MockPrintsCharming and issued a warning
    menu.pc.warning.assert_called_once()
    assert menu.pc is not None


def test_initialize_menus(mock_pc):
    # Provide an initial configuration
    initial_config = [
        ("main_menu", "vert", "Option1", "Option2", "Option3"),
        ("sub_menu", "hor", "SubOption1", "SubOption2")
    ]
    menu = InteractiveMenu(*initial_config)
    assert "main_menu" in menu.menus
    assert "sub_menu" in menu.menus
    assert menu.menu_types["main_menu"] == "vert"
    assert menu.menu_types["sub_menu"] == "hor"
    # Current menu should be set to the first one
    assert menu.current_menu == "main_menu"
    assert menu.menus["main_menu"] == ["Option1", "Option2", "Option3"]


def test_create_menu_invalid_type(mock_pc, capsys):
    menu = InteractiveMenu()
    menu.create_menu("weird_menu", "diagonal", ["X", "Y"])
    captured = capsys.readouterr()
    assert "Invalid menu type 'diagonal'" in captured.out


def test_switch_menu(mock_pc):
    menu = InteractiveMenu(
        ("main_menu", "vert", "A", "B"),
        ("second_menu", "vert", "C", "D")
    )
    assert menu.current_menu == "main_menu"
    menu.switch_menu("second_menu")
    assert menu.current_menu == "second_menu"
    # Stack should now contain the previous menu
    assert menu.menu_stack == ["main_menu"]


def test_go_back(mock_pc):
    menu = InteractiveMenu(
        ("main_menu", "vert", "A", "B"),
        ("second_menu", "vert", "C", "D")
    )
    menu.switch_menu("second_menu")
    menu.go_back()
    assert menu.current_menu == "main_menu"
    assert menu.menu_stack == []


def test_display_highlighted_menu(mock_pc):
    menu = InteractiveMenu(("main_menu", "vert", "Item1", "Item2"))
    menu.display_highlighted_menu()
    # The first item should have selected_style if set (None here, so no style)
    # and the second item should have unselected_style = 'default'
    # The mock_print calls can be inspected
    calls = [call.args for call in menu.pc.print.call_args_list]
    # calls look like [(display_text, {kwargs})]
    # We just check display text and the style argument
    assert "(1) Item1" in calls[0][0][0]
    assert "(2) Item2" in calls[1][0][0]


def test_navigate_vertical(mock_pc):
    menu = InteractiveMenu(("main_menu", "vert", "Item1", "Item2", "Item3"))
    # Initially selected_index = 0 (Item1)
    menu.navigate(1)  # Move down
    assert menu.selected_index == 1  # Item2 now selected
    menu.navigate(1)  # Move down again
    assert menu.selected_index == 2  # Item3 now selected
    menu.navigate(1)  # Should wrap around to top
    assert menu.selected_index == 0  # back to Item1


def test_navigate_horizontal(mock_pc):
    menu = InteractiveMenu(("color_menu", "hor", "Red", "Green", "Blue"))
    # Similar navigation logic for horizontal menus
    menu.navigate(1)
    assert menu.selected_index == 1  # Green
    menu.navigate(1)
    assert menu.selected_index == 2  # Blue
    menu.navigate(1)
    assert menu.selected_index == 0  # Wrap around to Red


def test_navigate_nested_menus(mock_pc):
    # Nested menu represented as a dict
    menu = InteractiveMenu(
        ("main_menu", "vert", "Option1", {"sub_menu": ["Sub1", "Sub2"]}, "Option2"),
        ("sub_menu", "vert", "Sub1", "Sub2")
    )
    assert menu.current_menu == "main_menu"
    menu.navigate(1)  # Move down from Option1 to sub_menu
    # Should have triggered switch_menu to sub_menu
    assert menu.current_menu == "sub_menu"


def test_run_quit(mock_pc):
    menu = InteractiveMenu(("main_menu", "vert", "Option1", "Option2"))
    # Press 'q' to quit
    inputs = ['q']
    with patch('interactive_menu.get_key', new=mock_get_key_sequence(inputs)):
        result = menu.run()
    assert result is None  # run should return None if quit is pressed


def test_run_confirm_option(mock_pc):
    menu = InteractiveMenu(("main_menu", "vert", "Option1", "Option2", "Option3"))
    # We'll navigate down once and confirm with '\r'
    # Navigation keys: 'j' moves down
    inputs = ['j', '\r']
    with patch('interactive_menu.get_key', new=mock_get_key_sequence(inputs)):
        result = menu.run()
    # We moved down once, so selected_index should have been 1 (Option2)
    # run returns selected_index + 1, so result should be 2
    assert result == 2


