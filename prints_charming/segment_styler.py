import re
import copy
import sys
from typing import Any, Dict, List, Tuple, Union, Optional





class SegmentStyler:
    def __init__(self, pc: "PrintsCharming"):
        self.pc = pc
        self.reset = self.pc.reset
        self.styles = self.pc.styles
        self.style_codes = self.pc.style_codes








    def segment_with_splitter_and_style(self,
                                        text: str,
                                        splitter_match: str,
                                        splitter_swap: Union[str, bool],
                                        splitter_show: bool,
                                        splitter_style: Union[str, List[str]],
                                        splitter_arms: bool,
                                        string_style: List[str]
                                        ) -> str:
        """
        Segments a text string using a specified splitter, applies style to
        each segment and splitter, and returns the styled result.

        This method splits `text` based on `splitter_match`, applies a list of
        styles to each segment and optionally to the splitter, then reassembles
        and returns the styled text.

        Parameters:
            text (str): The text to be segmented and styled.
            splitter_match (str): The string that identifies where to split `text`.
            splitter_swap (Union[str, bool]): The string to replace the splitter with;
                if set to False, `splitter_match` is used as the splitter.
            splitter_show (bool): Determines if the splitter should be included in
                the output between segments.
            splitter_style (Union[str, List[str]]): A single style or list of styles
                to apply to the splitter; if a list is provided, styles rotate
                across instances of the splitter.
            splitter_arms (bool): If True, applies styles to both the splitter
                and padding around it.
            string_style (List[str]): List of styles to apply to each segment;
                styles rotate across segments if the list length is shorter than
                the number of segments.

        Returns:
            str: The fully assembled, styled text with segments and splitters
            styled according to the parameters.

        """
        if isinstance(splitter_style, str):
            splitter_styles = [splitter_style]
        else:
            splitter_styles = splitter_style

        # Determine the actual splitter to use
        actual_splitter = splitter_swap if splitter_swap else splitter_match

        # Split the text based on the splitter_match
        segments = text.split(splitter_match)
        styled_segments = []

        for i, segment in enumerate(segments):
            # Apply string style to the segment
            segment_style = (
                string_style[i % len(string_style)]
                if string_style else 'default'
            )
            styled_segment = (
                f"{self.style_codes[segment_style]}{segment}{self.reset}"
            )
            #styled_segment = segment  # Start with the original segment

            if splitter_show and i > 0:

                if len(splitter_styles) == 1:
                    styled_splitter = (
                        f"{self.style_codes[splitter_styles[0]]}"
                        f"{actual_splitter}{self.reset}"
                    )
                else:
                    splitter_len = len(splitter_styles)
                    styled_splitter = (
                        f"{self.style_codes[splitter_styles[i % splitter_len]]}"
                        f"{actual_splitter}{self.reset}"
                    )
                    #styled_segment = styled_splitter + styled_segment

                # Apply the appropriate style to the splitter and padding
                if splitter_arms:
                    styled_segment = styled_splitter + styled_segment
                else:
                    styled_segment = actual_splitter + styled_segment

            styled_segments.append(styled_segment)

        return ''.join(styled_segments)


    # breaking changes i need to fix and combine with another one of these methods.
    def segment_and_style2(self,
                           text: str,
                           styles_dict: Dict[str, Union[str, int, List[Union[str, int]]]]
                           ) -> str:
        """
        Segments the input text and applies specified styles to words based on
        indices or word matches provided in a styles dictionary.

        This method splits the `text` into words, then applies styling to specific
        words according to `styles_dict`, where each style is associated with either
        word indices or word content. Optionally, a final style can be applied to
        any words not styled by previous operations.

        Parameters:
            text (str): The input text to be segmented and styled.
            styles_dict (Dict[str, Union[str, int, List[Union[str, int]]]]):
                A dictionary mapping styles to indices or words. Each key is a style,
                and each value indicates the words to style with that style.
                - If the value is an integer, it represents a 1-based index of a word
                  in `text` to style with the key's style.
                - If the value is a list, it can contain a mix of integers (1-based
                  indices) and words, where each item specifies words to style with
                  the corresponding key.
                - If the value is an empty string (""), the style will be applied as
                  the final style to any remaining unstyled words.

        Returns:
            str: The fully styled text, with each word styled according to the
            mappings specified in `styles_dict`.

        Example:
            Given `text = "This is a sample text"` and
            `styles_dict = {"bold": [1, "sample"], "italic": "", "underline": 3}`,
            the method will:
            - Apply "bold" style to the 1st word and the word "sample".
            - Apply "underline" style to the 3rd word.
            - Apply "italic" style to any remaining unstyled words.

        """
        words = text.split()
        word_indices = {word: i for i, word in enumerate(words)}  # Map words to their indices
        operations = []

        final_style = None

        # Prepare operations by iterating over the styles_dict
        for style, value in styles_dict.items():
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, int):
                        operations.append((item - 1, style))  # Convert 1-based index to 0-based
                    elif item in word_indices:
                        operations.append((word_indices[item], style))
            else:
                if isinstance(value, int):
                    operations.append((value - 1, style))  # Convert 1-based index to 0-based
                elif value in word_indices:
                    operations.append((word_indices[value], style))
                elif value == '':  # Handle the final style indicated by an empty string
                    final_style = style

        # Sort operations by index
        operations.sort()

        # Initialize the styled words with the entire text unstyled
        styled_words = words.copy()

        # Apply styles in the correct order
        for i, (index, style) in enumerate(operations):
            prev_index = operations[i - 1][0] + 1 if i > 0 else 0
            for j in range(prev_index, index + 1):
                styled_words[j] = f"{self.style_codes[style]}{words[j]}{self.reset}"

        # Apply the final style to any remaining words after the last operation
        if final_style:
            last_index = operations[-1][0] if operations else 0
            for j in range(last_index + 1, len(words)):
                styled_words[j] = f"{self.style_codes[final_style]}{words[j]}{self.reset}"

        return " ".join(styled_words)



    def segment_and_style(self,
                          text: str,
                          styles_dict: Dict[str, Union[str, int]]
                          ) -> str:
        """
        Segments the input text and applies specified styles to words based on
        indices or word matches from a dictionary of styles.

        This method divides `text` into individual words, then iterates over
        `styles_dict` to apply styles to specific words, based on either their
        index or content. Additionally, a final style can be applied to all
        remaining words after the last specified index or match.

        Parameters:
           text (str): The input text to be segmented and styled.
           styles_dict (Dict[str, Union[str, int]]): A dictionary where each key
               is a style to apply, and each value specifies either the index
               or the word in `text` to which the style should be applied.
               - If the value is an integer, it represents a 1-based index of the
                 word in `text` to style with the corresponding style.
               - If the value is a string, it matches the word in `text` to style
                 with the corresponding style.
               - If the value is an empty string or `None`, the style will be applied
                 as the final style to all remaining unstyled words in `text`.

        Returns:
           str: The fully styled text, with each word styled according to the
           mappings specified in `styles_dict`.

        Example:
           Given `text = "This is a sample text"` and
           `styles_dict = {"bold": 1, "italic": "sample", "underline": ""}`,
           the method will:
           - Apply "bold" style to the 1st word ("This").
           - Apply "italic" style to the word "sample".
           - Apply "underline" style to any remaining words after "sample".

        """
        words = text.split()
        previous_index = 0
        value_style = None

        # Iterate over the styles_dict items
        for style, key in styles_dict.items():
            if key:  # If key is provided (not an empty string or None)
                if isinstance(key, int):  # Handle key as an index
                    key_index = key - 1  # Convert 1-based index to 0-based
                else:  # Handle key as a word (string)
                    try:
                        key_index = words.index(str(key), previous_index)
                    except ValueError:
                        continue  # If key is not found, skip to the next item

                # Apply the style to the words between previous_index and key_index
                for i in range(previous_index, key_index):
                    words[i] = f"{self.style_codes[style]}{words[i]}{self.reset}"

                # Apply the style to the key word itself
                words[key_index] = f"{self.style_codes[style]}{words[key_index]}{self.reset}"

                # Update previous_index to the current key_index + 1 for the next iteration
                previous_index = key_index + 1
            else:
                # This handles the case where the key is empty, meaning style from the last key to the end
                value_style = style

        # Apply the final style to the remaining words after the last key
        if value_style:
            for i in range(previous_index, len(words)):
                words[i] = f"{self.style_codes[value_style]}{words[i]}{self.reset}"

        return " ".join(words)


    # Work in progress made some breaking changes i need to correct.
    def segment_and_style_update(self, text: str, styles_dict: Dict[str, Union[str, int]]) -> str:
        """
        Segments the input text and applies specified styles to words based on
        indices or word matches from a dictionary of styles.

        This method divides `text` into individual words and spaces, then iterates over
        `styles_dict` to apply styles to specific words, based on either their
        index or content. Additionally, a final style can be applied to all
        remaining words after the last specified index or match.

        Parameters:
           text (str): The input text to be segmented and styled.
           styles_dict (Dict[str, Union[str, int]]): A dictionary where each key
               is a style to apply, and each value specifies either the index
               or the word in `text` to which the style should be applied.
               - If the value is an integer, it represents a 1-based index of the
                 word in `text` to style with the corresponding style.
               - If the value is a string, it matches the word in `text` to style
                 with the corresponding style.
               - If the value is an empty string or `None`, the style will be applied
                 as the final style to all remaining unstyled words in `text`.

        Returns:
           str: The fully styled text, with each word and space styled according to the
           mappings specified in `styles_dict`.
        """
        # Use regular expression to split the text into words and spaces
        words_and_spaces = re.findall(r'\S+|\s+', text)
        styled_tokens = [None] * len(words_and_spaces)
        word_indices = {}
        word_index = 0
        previous_token_index = -1  # Initialize to -1 to start from the beginning

        # First pass: Style words based on styles_dict and record their indices
        for i, token in enumerate(words_and_spaces):
            if not token.isspace():
                word_index += 1  # Increment word index
                applied_style = False
                for style, key in styles_dict.items():
                    if key:  # If key is provided (not empty or None)
                        style_code = self.style_codes.get(style, '')
                        if isinstance(key, int):
                            if key == word_index and style in self.styles:
                                styled_tokens[i] = f"{style_code}{token}{self.reset}"
                                word_indices[i] = style_code
                                previous_token_index = i
                                applied_style = True
                                break
                        else:  # key is a string (word match)
                            if token.strip() == key and style in self.styles:
                                styled_tokens[i] = f"{style_code}{token}{self.reset}"
                                word_indices[i] = style_code
                                previous_token_index = i
                                applied_style = True
                                break
                if not applied_style:
                    styled_tokens[i] = token
                    word_indices[i] = None
            else:
                # Temporarily store spaces; we'll handle them in the next pass
                styled_tokens[i] = token

        # Second pass: Apply styles to words between specified indices or words
        last_style = None
        last_key_index = -1
        for style, key in styles_dict.items():
            if key:  # If key is provided
                style_code = self.style_codes.get(style, '')
                if isinstance(key, int):
                    key_indices = [i for i, idx in enumerate(word_indices.values()) if idx == style_code]
                else:
                    key_indices = [i for i, token in enumerate(words_and_spaces) if token.strip() == key]
                if key_indices:
                    key_index = key_indices[0]
                    # Apply style to tokens between last_key_index and key_index
                    for i in range(last_key_index + 1, key_index):
                        if styled_tokens[i] is None and not words_and_spaces[i].isspace():
                            styled_tokens[i] = f"{style_code}{words_and_spaces[i]}{self.reset}"
                            word_indices[i] = style_code
                    last_key_index = key_index
                    last_style = style_code
            else:
                # Store the last style code for final styling
                last_style = self.style_codes.get(style, '')

        # Apply final style to remaining unstyled words after the last key
        if last_style:
            for i in range(last_key_index + 1, len(words_and_spaces)):
                if styled_tokens[i] is None and not words_and_spaces[i].isspace():
                    styled_tokens[i] = f"{last_style}{words_and_spaces[i]}{self.reset}"
                    word_indices[i] = last_style

        # Third pass: Style spaces based on adjacent words
        for i, token in enumerate(words_and_spaces):
            if token.isspace():
                prev_style = word_indices.get(i - 1)
                next_style = word_indices.get(i + 1)
                if prev_style == next_style and prev_style is not None:
                    # If both adjacent words have the same style, use it
                    styled_tokens[i] = f"{prev_style}{token}{self.reset}"
                elif prev_style is not None:
                    # If only the previous word is styled, use its style
                    styled_tokens[i] = f"{prev_style}{token}{self.reset}"
                elif next_style is not None:
                    # If only the next word is styled, use its style
                    styled_tokens[i] = f"{next_style}{token}{self.reset}"
                else:
                    # Leave space unstyled
                    pass
            else:
                if styled_tokens[i] is None:
                    # Ensure any unstyled tokens are assigned
                    styled_tokens[i] = words_and_spaces[i]

        return ''.join(styled_tokens)


    # Special method called by the print method when style param is a dict
    # Does not style spaces only words
    def _style_words_by_index(self,
                              text: str, style: Dict[Union[int, Tuple[int, int]], str]
                              ) -> str:
        """
        Styles words in the text based on their index or a range of indices.

        :param text: The input text to style.
        :param style: A dictionary mapping indices or index ranges to style names.
        :return: The styled text.
        """

        words = text.split()

        for i, word in enumerate(words, start=1):  # Start indexing from 1
            for key in style:
                style_name = style[key]
                style_code = self.style_codes[style_name]
                if isinstance(key, tuple):
                    start, end = key
                    if start <= i <= end and style_name in self.styles:  # Inclusive end
                        words[i - 1] = f"{style_code}{word}{self.reset}"
                elif isinstance(key, int):
                    if key == i and style_name in self.styles:
                        words[i - 1] = f"{style_code}{word}{self.reset}"

        return " ".join(words)


    # Public facing method that accounts for whitespace and styles it and words.
    def style_words_by_index(self, text: str, style: Dict[Union[int, Tuple[int, int]], str]) -> str:
        """
        Styles words and whitespace in the text based on their index or a range of indices.

        :param text: The input text to style.
        :param style: A dictionary mapping indices or index ranges to style names.
        :return: The styled text.
        """
        words_and_spaces = re.findall(r'\S+|\s+', text)
        styled_words_and_spaces = [None] * len(words_and_spaces)
        word_indices: Dict[int, Optional[str]] = {}
        word_index = 0

        # First pass: style words and record their indices
        for i, token in enumerate(words_and_spaces):
            if not token.isspace():
                word_index += 1
                applied_style = False
                for key in style:
                    style_name = style[key]
                    style_code = self.style_codes.get(style_name, '')
                    if isinstance(key, tuple):
                        start, end = key
                        if start <= word_index <= end and style_name in self.styles:
                            styled_words_and_spaces[i] = f"{style_code}{token}{self.reset}"
                            word_indices[i] = style_code
                            applied_style = True
                            break
                    elif isinstance(key, int):
                        if key == word_index and style_name in self.styles:
                            styled_words_and_spaces[i] = f"{style_code}{token}{self.reset}"
                            word_indices[i] = style_code
                            applied_style = True
                            break
                if not applied_style:
                    styled_words_and_spaces[i] = token
                    word_indices[i] = None
            else:
                # Temporarily store spaces as is; we'll handle them in the next pass
                styled_words_and_spaces[i] = token


        # Second pass: style spaces based on adjacent words
        for i, token in enumerate(words_and_spaces):
            if token.isspace():
                prev_style = word_indices.get(i - 1)
                next_style = word_indices.get(i + 1)
                if prev_style == next_style and prev_style is not None:
                    # If both adjacent words have the same style, use it
                    styled_words_and_spaces[i] = f"{prev_style}{token}{self.reset}"
                elif prev_style is not None:
                    # If only the previous word is styled, use its style
                    styled_words_and_spaces[i] = f"{prev_style}{token}{self.reset}"
                elif next_style is not None:
                    # If only the next word is styled, use its style
                    styled_words_and_spaces[i] = f"{next_style}{token}{self.reset}"
                else:
                    # Leave space unstyled
                    pass


        return ''.join(styled_words_and_spaces)














