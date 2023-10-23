#!/usr/bin/env python3

from ..prints_charming import TextStyle, ColorPrinter

# To run this script as a module inside the package. Navigate to the top-level directory and run
# python -m prints_charming.examples.main

config = {
    "color_text"          : True,
    "args_to_strings"     : True,
    "style_names"         : True,
    "style_words_by_index": True,
    "kwargs"              : True,
    "conceal"             : True,
    "width"               : 80,
}

styles = {
    "default"      : TextStyle(),
    "white"        : TextStyle(color="white"),
    "gray"         : TextStyle(color="gray"),
    "green"        : TextStyle(color="green"),
    "vgreen"       : TextStyle(color="vgreen"),
    "red"          : TextStyle(color="red"),
    "vred"         : TextStyle(color="vred", bold=True, italic=True, underlined=True, overlined=True, blink=True),
    "blue"         : TextStyle(color="blue"),
    "vblue"        : TextStyle(color="vblue"),
    "yellow"       : TextStyle(color="yellow"),
    "vyellow"      : TextStyle(color="vyellow"),
    "cyan"         : TextStyle(color="cyan"),
    "vcyan"        : TextStyle(color="vcyan"),
    "magenta"      : TextStyle(color="magenta", bold=True, underlined=True),
    "pink"         : TextStyle(color="pink"),
    "purple"       : TextStyle(color="purple", bg_color="gray", reversed=True),
    "orange"       : TextStyle(color="orange"),
    "header_text"  : TextStyle(color="white", bg_color="purple", bold=True, reversed=True),
    "header_symbol": TextStyle(color="magenta", bold=True, overlined=True, strikethrough=True),
    "task"         : TextStyle(color="blue", bold=True),
    "conceal"      : TextStyle(conceal=True),
}

colorprinter_variables = {
    "vgreen": ["Hello, world!", "Connected", "Loaded", "Monitor", "ABOVE THRESHOLD", "wss://advanced-trade-ws.coinbase.com", "Starting", "True"],
    "vred": ["Failed!", "Error", "Failed", "None", "Skipping.", "Canceling", "Canceled"],
    "blue": ["CoinbaseWebsocketClient", "server"],
    "yellow": ["1", "returned",],
    "vyellow": ["File modified:", "File modified AGAIN", "subscribed"],
    "magenta": ["within 10 seconds."],
    "cyan": ["|", "#"],
    "orange": ["New Message!"],
    "purple": ["My background is purple"]
    # Uncomment the next line to hide API keys or sensitive information
    #"conceal": [os.environ[key] for key in os.environ if "API" in key],
}

# Create an instance of the ColorPrinter class with default colormap, custom config, and custom styles
cp = ColorPrinter(config=config, styles=styles)

# Print all the foreground colors in the color map with it's name to the right of it.
# You can supply your own color_map as an arg in the init method.
# For styling of the first cp.print statement we will add 'Name:' to the word map.
cp.print("##############################################################################################", color="yellow")
cp.print("#### Print all the foreground colors in the color map each with it's name to the right of it.", color="yellow")
cp.print("#### You can optionally supply your own color_map as an arg in the init method.", color="yellow")
cp.print("#### For styling of the first cp.print statement we will add 'Name:' to the word map.", color="yellow")
cp.print("##############################################################################################", color="yellow")
cp.add_variable("Name:", style_name="default")
for color_name, color_code in cp.color_map.items():
    cp.print(f"### This is one of the prints_charming foreground colors in the color map. ### Name: {color_name}", color=color_name)

# Print all the styles in the styles dictionary with it's name to the right of it.
# As you can see most of the styles are named after the foreground color, but you can edit the styles and name them whatever you want!
# You can supply your own styles dictionary as an arg in the init method as I have done here, but if you don't this is also the default.
cp.print("##############################################################################################", color="yellow")
cp.print("#### Print all the styles in the styles dictionary each with it's name to the right of it.", color="yellow")
cp.print("#### As you can see most of the styles in this example are named after the foreground color.", color="yellow")
cp.print("#### You can optionally supply your own styles dictionary or not and go with the default.", color="yellow")
cp.print("#### You can edit the styles and name them whatever you want!", color="yellow")
cp.print("##############################################################################################", color="yellow")
for style_name, style in cp.styles.items():
    cp.print(f"### This is one of the prints_charming above defined styles! ### Name: {style_name}", style=style_name)

# Print all the computed background colors from the color map dictionary.
cp.print("############################################################################", color="yellow")
cp.print("#### Print all the computed background colors from the color map dictionary.", color="yellow")
cp.print("############################################################################", color="yellow")
for color in cp.color_map:
    cp.print_bg(color, length=80)

# Basic printing with ColorPrinter will print in the default style with default color.
cp.print("# Basic printing with ColorPrinter will print in the default style with default color.")
cp.print("Hello, world!")

# Print in the default style reversed foreground and background.
cp.print("#  Print in the default style reversed foreground and background.")
cp.print("Hello, world!", reversed=True)

# Specify only the color of the args.
cp.print("# Specify only the color of the args.")
cp.print("Hello, world!", color="red")

# Specify only italic and underlined will print in the default color.
cp.print("# Specify only italic and underlined will print in the default color.")
cp.print("Hello, world!", italic=True, underlined=True)

# Specify a predefined style 'magenta'. The 'magenta' style is defined above.
cp.print("# Specify a predefined style 'magenta'. The 'magenta' style is defined above.")
cp.print("Hello, world!", style="magenta")

# Specify predefined style 'task' for printing. The 'task' style is defined above.
cp.print("# Specify predefined style 'task' for printing. The 'task' style is defined above.")
cp.print("This is a task.", style="task")

# Specify predefined style 'task' for printing. But change color to green and underlined to True.
cp.print("# Specify predefined style 'task' for printing. But change color to green and underlined to True.")
cp.print("This is a task.", style ="task", color="green", underlined=True)

# Show that 'Hello, world!' isn't color or style defined.
cp.print("# Show that 'Hello, world!' isn't color or style defined.")
cp.print("Hello, world!")

# Use the add_variable method to add 'Hello, world!' to the phrases dictionary with 'vgreen' style.
cp.print("# Use the add_variable method to add 'Hello, world!' to the phrases dictionary with 'vgreen' style.")
cp.add_variable("Hello, world!", style_name="vgreen")

# Show that 'Hello, world!' is style defined in the phrases dictionary.
cp.print("# Show that 'Hello, world!' is style defined in the phrases dictionary.")
cp.print("Hello, world!")

# Use the remove_variable method to remove 'Hello, world!' from the styled phrases dictionary.
cp.print("# Use the remove_variable method to remove 'Hello, world!' from the styled phrases dictionary.")
cp.remove_variable("Hello, world!")

# Show that 'Hello, world!' has been removed from the styled phrases dictionary.
cp.print("# Show that 'Hello, world!' has been removed from the styled phrases dictionary.")
cp.print("Hello, world!")

# Define a variable.
cp.print("# Define a variable.")
text = "Hello, world!"

# Use the add_variable method to add {text} to the phrases dictionary with 'yellow' style.
cp.print("# Use the add_variable method to add {text} to the phrases dictionary with 'yellow' style.")
cp.add_variable(text, style_name="yellow")

# Show that 'Hello, world!' is style defined in the phrases dictionary.
cp.print("# Show that 'Hello, world!' is style defined in the phrases dictionary.")
cp.print(text)

# Show that 'Hello, world!' retains it's style while other words are unstyled.
cp.print("# Show that 'Hello, world!' retains it's style while other words are unstyled.")
cp.print(f"This sentence says, {text}")

# Show how you can style other words alongside, 'Hello, world!'.
cp.print("# Show how you can style other words alongside, 'Hello, world!'.")
cp.print(f"This sentence says, {text}", style='task')

# Show how the order of the words doesn't matter.
cp.print("# Show how the order of the words doesn't matter.")
cp.print(f"{text} Let me say that again, {text} {text} I said it again!", style="orange")

# Use the remove_variable method to remove 'Hello, world!' from the styled phrases dictionary.
cp.print("# Use the remove_variable method to remove 'Hello, world!' from the styled phrases dictionary.")
cp.remove_variable("Hello, world!")

# Show that 'Hello, world!' has been removed from the styled phrases dictionary.
cp.print("# Show that 'Hello, world!' has been removed from the styled phrases dictionary.")
cp.print("Hello, world!")

# Show how to style words by index.
cp.print("# Show how to style words by index.")
cp.print(f"These words are going to be styled by their indexes",
         style={0:"vgreen", (1,4):"blue", (4,6):"yellow", 6:"purple", (7,10):"pink"})

# Printing styled variables in the middle of a string with text substitution without having to add the variable to the cp instance.
cp.print("# Printing styled variables in the middle of a string with text substitution without having to add the variable to the cp instance.")
# 'var' in text is subbed with the value of balance.
cp.print("# 'var' in text is subbed with the value of balance.")
balance = 1.25
cp.print(text=f"Value: var USD", var=balance, tstyle='orange', vstyle='vgreen')

# Now let's add some predefined words and phrases to our word and phrase map for automatic styling.
cp.print("# Now let's add some predefined words and phrases to our word and phrase map for automatic styling.")
cp.add_variables_from_dict(colorprinter_variables)

# Show printing text that will be automatically styled from the word and phrase maps created from the colorprinter_variables above.
cp.print("# Show printing text that will be automatically styled from the word and phrase maps created from the colorprinter_variables above.")
cp.print(f"Let's first print, Hello, world! styled as described above.")

# Show printing text same as above but adding additional style to the rest of the text.
cp.print("# Show printing text same as above but adding additional style to the rest of the text.")
cp.print(f"Let's first print, Hello, world! styled as described above and right here.", style="yellow")

# Show printing text same as above but include text from multiple phrases/words in the maps.
cp.print("# Show printing text same as above but include text from multiple phrases/words in the maps.")
cp.print(f"{text} Remember we assigned, 'Hello, world!' to the 'text' variable above. Let's pretend we are Connected to wss://advanced-trade-ws.coinbase.com", color="blue")

# Let's mix and match. Here we will combine the above with styling by index.
cp.print("# Let's mix and match. Here we will combine the above with styling by index.")
cp.print(f"These words are going to be styled by their indexes, {text}",
         style={0:"vgreen", (1,4):"blue", (4,6):"yellow", 6:"purple", (7,10):"pink"})

# What do you think will happen here?
cp.print("# What do you think will happen here?")
# When coloring by index, coloring by index takes precedence.
cp.print("# When coloring by index, coloring by index takes precedence.")
cp.print(f"{text} These words are going to be styled by their indexes, {text}",
         style={0:"vgreen", (1,4):"blue", (4,6):"yellow", 6:"purple", (7,10):"pink"})

# So to combine the two correctly we would have to do this.
cp.print("# So to combine the two correctly we would have to do this.")
cp.print(f"{text} Only these words are going to be styled by their indexes, {text}",
         style={(2,4):"orange", (4,7):"blue", (7,9):"yellow", 9:"purple", (10,13):"pink"})

# Print different styled automatically styled text.
cp.print(f"Let's try, New Message! Let's try, True and 1 and | and Failed! File modified: is this an Error Monitor My background is purple these words are default. server")

# Same but specify a style for other words/phrases
cp.print(f"Let's try, New Message! Let's try, True and 1 and | and Failed! File modified: is this an Error Monitor My background is purple these words are magenta. server", style='magenta')

# Using Dictionary with print_variables method
vars_and_styles_dict = {
    "balance" : (1000, "green"),
    "username": ("Prince Charming", "blue")
}
cp.print_variables(vars_and_styles_dict, "Hello {username}, your balance is {balance} USD.", text_style="yellow")


# Using Lists with print_variables method
vars_and_styles_list = ([1000, "Cinderella"], ["green", "blue"])
cp.print_variables(vars_and_styles_list, "Hello var2, your balance is var1 USD.", text_style="yellow")

# Print word map
cp.pretty_print_cp_map(cp.word_map, style_name="default")

# Print phrase map
cp.pretty_print_cp_map(cp.phrase_map, style_name="default")

# Print conceal map
cp.pretty_print_cp_map(cp.conceal_map, style_name="default")

# Sample table data
table_data = [
    ["Name", "Age", "Occupation"],
    ["Prince Charming", 27, "Prince"],
    ["Cinderella", 21, "Princess"],
    ["Anastasia", 24, "Socialite"],
    ["Drizella", 22, "Socialite"]
]

# Print a table
cp.print_table(table_data, header_style="magenta", border_style="green")

