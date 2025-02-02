
from prints_charming import (
    #MarkDown,
    PStyle,
    PrintsCharming,
    FrameBuilder,
    InteractiveMenu,
    TableManager
)

#import JavaScriptHighlighter

#from configs import js_config




class CustomPrintsCharming(PrintsCharming):
    def __init__(self) -> None:
        super().__init__()
        #self.md = MarkDown(self)
        self.builder = FrameBuilder(self)
        self.table_manager = TableManager(self)
        self.menus = {}
        self.configure_markdown()




    def configure_markdown(self) -> None:
        #self.md.register_highlighter('javascript', JavaScriptHighlighter(js_config))
        pass


    def create_menu(self, name) -> None:
        pass


##############################
# Scenarios definition
##############################

# Scenario 1: A simple vertical menu
scenario_1_menus = [
    ("simple_vertical", "vert", "Option A", "Option B", "Back")
]

# Scenario 2: A horizontal menu
scenario_2_menus = [
    ("simple_horizontal", "hor", "Alpha", "Beta", "Gamma", "Delta", "Back")
]

# Scenario 3: A nested vertical menu
scenario_3_menus = [
    (
        "main_menu", "vert",
        "First",
        "Second", {
            "nested_1": [
                "N1_Option1",
                "N1_Option2",
                "Back"
            ]
        },
        "Back"
    ),
    (
        "nested_1", "vert",
        "Nested1_A",
        "Nested1_B",
        "Back"
    )
]


# Scenario 4: Complex scenario with multiple nesting and horizontal/vertical mix
scenario_4_menus = [
    ("main_menu", "vert", "Start", "Settings", {"More Options": ["Extra1", "Extra2", {"Deep Nested": ["DN1", "DN2"]}]}, "Back"),
    ("Settings", "vert", "Audio", "Video", "Back"),
    ("More Options", "vert", "Extra1", "Extra2", {"color_menu": ["Red", "Green", "Blue"]}, "Back"),
    ("color_menu", "hor", "Red", "Green", "Blue"),
    ("Deep Nested", "vert", "DN1", "DN2", "Back")
]

scenario_5_menus = [
    ("simple_horizontal", "hor", "Alpha", {"Beta": ["Beta_1", "Beta_2", "Beta_3"]}, "Gamma", "Delta", "Back"),
]


##############################
# Aggregator menu definition
##############################
# The aggregator menu allows choosing which scenario to run.
aggregator_menus = [
    ("aggregator", "vert",
     "Run Simple Vertical Scenario",
     "Run Simple Horizontal Scenario",
     "Run Nested Scenario",
     "Run Complex Scenario",
     "Run Scenario 5 menu",
     "Quit")
]

##############################
# Main logic:
# 1. Start with aggregator menu.
# 2. On selection, run the chosen scenario.
# 3. Allow "Back" from scenario to aggregator again.
##############################


##############################
# Run scenario helper
##############################
def run_scenario(initial_menus):
    # If user presses 'q', scenario.run() returns None
    # If user selects 'Back' on the top-level menu, scenario.run() returns the index for 'Back'.
    # In both cases, we return to aggregator.
    scenario = InteractiveMenu(
        *initial_menus,
        selected_style='vcyan',
        unselected_style='default',
        confirmed_style='vgreen',
        alt_buffer=True,
    )
    scenario_result = scenario.run()
    # scenario_result is None if 'q' pressed, or an integer representing the chosen option if Enter pressed.
    # If user chose "Back" at top-level menu, we also return to aggregator.
    return  # Back to aggregator after scenario


def main():
    while True:
        # Run aggregator
        aggregator = InteractiveMenu(
            *aggregator_menus,
            selected_style='vcyan',
            unselected_style='default',
            confirmed_style='vgreen',
            alt_buffer=True,
        )
        choice = aggregator.run()

        # If user pressed 'q' at aggregator, choice is None
        if choice is None:
            # User pressed q in aggregator, exit
            break

        # choice corresponds to the chosen line (1-based)
        if choice == 1:
            run_scenario(scenario_1_menus)
        elif choice == 2:
            run_scenario(scenario_2_menus)
        elif choice == 3:
            run_scenario(scenario_3_menus)
        elif choice == 4:
            run_scenario(scenario_4_menus)
        elif choice == 5:
            run_scenario(scenario_5_menus)
        elif choice == 6:
            # Quit aggregator
            break
        # After scenario returns, we loop again to aggregator
    # Exiting main ends the program.


if __name__ == "__main__":
    main()

