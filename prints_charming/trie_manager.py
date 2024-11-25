# trie_manager.py

import re
from typing import Any, Dict, List, Optional, Set, Tuple, Union



class KeyTrieNode:
    def __init__(self):
        self.children = {}
        self.categories = {}
        self.is_end = False
        self.style_info = None
        self.insertion_order = None


class KeyTrie:
    def __init__(self):
        self.root = KeyTrieNode()
        self.insertion_counter = 0

    def insert(self, text, style_info):
        node = self.root
        for char in text:
            if char not in node.children:
                node.children[char] = KeyTrieNode()
            node = node.children[char]
        node.is_end = True
        node.style_info = style_info
        node.insertion_order = self.insertion_counter
        self.insertion_counter += 1


    def search_prefix(self, text):
        node = self.root
        current_match = []
        for char in text:
            if char not in node.children:
                break
            node = node.children[char]
            current_match.append(char)
            if node.is_end:
                return ''.join(current_match), node.style_info
        return None  # No prefix


    def search_longest_prefix(self, text, normalize=False, normalize_sep=' '):
        original_text = text  # Store the original unnormalized text

        if normalize:
            # Normalize the search text by replacing \n and \t with ' '
            text = text.replace('\n', ' ').replace('\t', ' ')

            # Normalize spaces
            text = re.sub(r'\s+', normalize_sep, text)

        node = self.root
        longest_match = None
        current_match = []

        # Track the length of the match to map back to original text
        match_length_original = 0

        for char in text:
            if char not in node.children:
                break
            node = node.children[char]
            current_match.append(char)

            match_length_original += 1

            if node.is_end:
                longest_match = (''.join(current_match), node.style_info)

        if longest_match:
            # Map the matched portion back to the original unnormalized text
            # Extract original matched text
            original_match = original_text[:match_length_original]

            # Return original match with style info
            return original_match, longest_match[1]



    def search_suffix(self, text):
        matches = []
        for i in range(len(text)):
            node = self.root
            current_match = []
            for j in range(i, len(text)):
                char = text[j]
                if char not in node.children:
                    break
                node = node.children[char]
                current_match.append(char)
                if node.is_end:
                    matches.append((''.join(current_match), node.style_info))
        # Now check if any match is at the end of the word
        for match, style_info in matches:
            if text.endswith(match):
                return match, style_info
        return None  # No suffix match found


    def search_any_substring(self, text):
        # Search for any substring match within the given text
        matches = []
        for i in range(len(text)):
            node = self.root
            current_match = []
            for j in range(i, len(text)):
                char = text[j]
                if char not in node.children:
                    break
                node = node.children[char]
                current_match.append(char)
                if node.is_end:
                    matches.append((''.join(current_match), node.style_info))
        return matches if matches else None


    def search_any_substring_by_insertion_order(self, text):
        # Search for any substring match within the given text
        matches = []
        for i in range(len(text)):
            node = self.root
            current_match = []
            for j in range(i, len(text)):
                char = text[j]
                if char not in node.children:
                    break
                node = node.children[char]
                current_match.append(char)
                if node.is_end:
                    matches.append((''.join(current_match), node.style_info, node.insertion_order))

        # Sort matches by the insertion order to prioritize the earliest added
        # substring
        matches.sort(key=lambda x: x[2])  # Sort by insertion_order
        return matches if matches else None


    def search(self, text):
        node = self.root
        for char in text:
            if char not in node.children:
                return None  # Phrase not found
            node = node.children[char]
        return node.style_info if node.is_end else None



class TrieManager:
    def __init__(self, pc_instance):
        self.pc = pc_instance  # Reference to PrintsCharming instance
        self.phrase_trie = None
        self.shortest_phrase_length = None
        self.word_trie = None
        self.word_map = {}
        self.subword_trie = None
        self.enable_styled_phrases = False
        self.enable_styled_words = False
        self.enable_word_trie = False
        self.enable_word_map = False
        self.enable_styled_subwords = False
        self.enable_styled_variable_map = False
        self.sentence_ending_characters = ".,!?:;"



    def add_subword(
        self,
        subword: str,
        style_name: str,
        handle_reverse: bool = True,
        enable_trie: bool = True
    ) -> None:
        """
        Adds a subword to the subword trie with a specific style.

        :param subword: The subword to be styled.
        :param style_name: The name of the style to apply.
        :param handle_reverse: Reverse color and bg_color attribs for properly
                               integrating smooth style transitions in text with
                               share-alike params in final styled text.
        :param enable_trie: set self.enable_styled_subwords flag.
        """

        subword = str(subword)
        if style_name in self.pc.styles:

            # Get the style attributes
            attribs = vars(self.pc.styles.get(style_name)).copy()
            if attribs.get('reversed') and handle_reverse:
                attribs['color'], attribs['bg_color'] = (
                    attribs.get('bg_color'), attribs.get('color')
                )

            if not self.subword_trie:
                # Create subword trie
                self.subword_trie = KeyTrie()

            # Insert the subword into the subword trie
            self.subword_trie.insert(subword, {
                "style": style_name,
                "style_code": self.pc.style_codes[style_name],
                "attribs": attribs
            })

            # Enable the subwords flag
            if not self.enable_styled_subwords and enable_trie:
                self.enable_styled_subwords = True
                self.pc.print(f"self.enable_styled_subwords = True")
        else:
            print(f"Style {style_name} not found in styles dictionary.")


    def add_subwords(
        self,
        subwords: List[str],
        style_name: str,
        handle_reverse: bool = True,
        enable_trie: bool = True
    ) -> None:
        """
        Adds a list of subwords to the subword trie with style information.

        :param subwords: A list of subwords to be styled.
        :param style_name: The name of the style to apply.
        :param handle_reverse: Reverse color and bg_color attribs for properly
                               integrating smooth style transitions in text with
                               share-alike params in final styled text.
        :param enable_trie: set self.enable_styled_subwords flag.
        """

        if style_name in self.pc.styles:
            style_code = self.pc.style_codes[style_name]
            for subword in subwords:
                self.add_subword(
                    subword,
                    style_name,
                    handle_reverse=handle_reverse,
                    enable_trie=enable_trie,
                )


    def add_subwords_from_dict(
        self,
        subwords_dict: Dict[str, List[str]],
        handle_reverse: bool = True,
        enable_trie: bool = True,
    ) -> None:
        """
        Adds subwords to the subword trie with style information

        :param subwords_dict: A dictionary where keys are style names and
                              values are lists of subwords.
        :param handle_reverse: Reverse color and bg_color attribs for properly
                               integrating smooth style transitions in text with
                               share-alike params in final styled text.
        :param enable_trie: set self.enable_styled_subwords flag.
        """
        for style_name, subwords in subwords_dict.items():
            if style_name in self.pc.styles:
                self.add_subwords(
                    subwords,
                    style_name,
                    handle_reverse=handle_reverse,
                    enable_trie=enable_trie,
                )
            else:
                print(f"Style {style_name} not found in styles dictionary.")


    def add_string(self,
                   string: str,
                   style_name: str,
                   word_trie: bool = False,
                   handle_reverse: bool = True,
                   enable_phrase_trie: bool = True,
                   enable_word_trie: bool = True,
                   enable_word_map: bool = True,
                   ) -> None:
        """
        Adds a string (word or phrase) to the appropriate trie with a specific
        style.

        :param string: The string to be styled.
        :param style_name: The name of the style to apply.
        :param word_trie: Insert in word_trie if True otherwise word_map
        :param handle_reverse: Reverse color and bg_color attribs for properly
                               integrating smooth style transitions in text with
                               share-alike params in final styled text.
        :param enable_phrase_trie: set self.enable_styled_phrases flag.
        :param enable_word_trie: set self.enable_styled_words flag.
        :param enable_word_map: set self.enable_word_map flag.
        """

        string = str(string)
        if style_name in self.pc.styles:
            style_code = self.pc.get_style_code(style_name)
            styled_string = f"{style_code}{string}{self.pc.reset}"

            # Copy the style attributes
            attribs = vars(self.pc.styles.get(style_name)).copy()
            if attribs.get('reverse') and handle_reverse:
                attribs['color'], attribs['bg_color'] = (
                    attribs.get('bg_color'), attribs.get('color')
                )

            # Determine if the string is a phrase (contains inner spaces)
            contains_inner_space = ' ' in string.strip()

            if contains_inner_space:
                # It's a phrase
                if not self.phrase_trie:
                    # Create phrase trie
                    self.phrase_trie = KeyTrie()

                # Create phrase words and spaces list
                phrase_words_and_spaces = (
                    self.pc.get_words_and_spaces(string)
                )
                phrase_length = len(phrase_words_and_spaces)
                if not self.shortest_phrase_length:
                    self.shortest_phrase_length = phrase_length
                else:
                    if phrase_length < self.shortest_phrase_length:
                        self.shortest_phrase_length = phrase_length

                # Insert the phrase into the phrase trie
                self.phrase_trie.insert(string, {
                    "phrase_words_and_spaces": phrase_words_and_spaces,
                    "phrase_length": phrase_length,
                    "style": style_name,
                    "style_code": style_code,
                    "styled": styled_string,
                    "attribs": attribs
                })
                if not self.enable_styled_phrases and enable_phrase_trie:
                    self.enable_styled_phrases = True
            else:
                if word_trie:
                    if not self.word_trie:
                        # Create word trie
                        self.word_trie = KeyTrie()
                    # Insert the word into the word trie
                    self.word_trie.insert(string, {
                        "style": style_name,
                        "style_code": style_code,
                        "styled": styled_string,
                        "attribs": attribs
                    })
                    if not self.enable_word_trie and enable_word_trie:
                        self.enable_word_trie = True
                else:
                    # Insert the word into the word map
                    self.word_map[string] = {
                        "style": style_name,
                        "style_code": style_code,
                        "styled": styled_string,
                        "attribs": attribs
                    }
                    if not self.enable_word_map and enable_word_map:
                        self.enable_word_map = True

                if (
                    not self.enable_styled_words
                    and (enable_word_trie or enable_word_map)
                ):
                    self.enable_styled_words = True

        else:
            print(f"Style {style_name} not found in styles dictionary.")


    def add_strings(self,
                    strings: List[str],
                    style_name: str,
                    word_trie: bool = False,
                    handle_reverse: bool = True,
                    enable_phrase_trie: bool = True,
                    enable_word_trie: bool = True,
                    enable_word_map: bool = True,
                    ) -> None:
        """
        Adds a list of strings (can be a mix of phrases and words) to an
        instance trie or dictionary depending on if it is a phrase (contains
        one or more ' ' characters) then will be added to self.phrase_trie or
        if it is a word (does not contain any ' ' characters) then it is added
        to self.word_map unless word_trie param is set to True which in that
        case the word will be added to self.word_trie.

        :param strings: A list of strings to be styled.
        :param style_name: The name of the style to apply.
        :param word_trie: If True, insert words into the word trie; otherwise,
                          use word_map.
        :param handle_reverse: Reverse color and bg_color attribs for properly
                               integrating smooth style transitions in text with
                               share-alike params in final styled text.
        :param enable_phrase_trie: set self.enable_styled_phrases flag.
        :param enable_word_trie: set self.enable_styled_words flag.
        :param enable_word_map: set self.enable_word_map flag.
        """
        if style_name in self.pc.styles:
            style_code = self.pc.style_codes[style_name]
            for string in strings:
                self.add_string(
                    string,
                    style_name,
                    word_trie,
                    handle_reverse,
                    enable_phrase_trie,
                    enable_word_trie,
                    enable_word_map
                )


    def add_strings_from_dict(
            self,
            strings_dict: Dict[str, List[str]],
            word_trie: bool = False,
            handle_reverse: bool = True,
            enable_phrase_trie: bool = True,
            enable_word_trie: bool = True,
            enable_word_map: bool = True,
    ) -> None:
        """
        Adds strings (can be a mix of phrases and words) to an instance trie or
        dictionary depending on if it is a phrase (contains one or more ' '
        characters) then will be added to self.phrase_trie or if it is a word
        (does not contain any ' ' characters) then it is added to
        self.word_map unless word_trie param is set to True which in that case
        the word will be added to self.word_trie.

        :param strings_dict: A dictionary where keys are style names and values
                             are lists of strings.
        :param word_trie: If True, insert words into the word trie; otherwise,
                          use word_map.
        :param handle_reverse: Reverse color and bg_color attribs for properly
                               integrating smooth style transitions in text with
                               share-alike params in final styled text.
        :param enable_phrase_trie: set self.enable_styled_phrases flag.
        :param enable_word_trie: set self.enable_styled_words flag.
        :param enable_word_map: set self.enable_word_map flag.
        """
        for style_name, strings in strings_dict.items():
            if style_name in self.pc.styles:
                self.add_strings(
                    strings,
                    style_name,
                    word_trie,
                    handle_reverse,
                    enable_phrase_trie,
                    enable_word_trie,
                    enable_word_map
                )
            else:
                print(f"Style {style_name} not found in styles dictionary.")


    def remove_string(self, string: str) -> None:
        """
        Removes a string (word or phrase) from the appropriate trie or map.

        :param string: The string to be removed.
        """

        string = str(string)

        # Determine if the string is a phrase (contains inner spaces)
        contains_inner_space = ' ' in string.strip()

        if contains_inner_space:
            # Remove from the phrase trie if present
            if (
                self.phrase_trie
                and self._remove_from_trie(self.phrase_trie, string)
            ):
                print(f"Removed '{string}' from phrase trie")

        else:

            if self.enable_word_trie:
                # Remove from the word trie if present
                if (
                    self.word_trie
                    and self._remove_from_trie(self.word_trie, string)
                ):
                    print(f"Removed '{string}' from word trie")

            if self.enable_word_map:
                # Remove from the word map if present
                if self.word_map and self._remove_word(string):
                    print(f"Removed '{string}' from word map")


    def _remove_from_trie(self, trie: KeyTrie, string: str) -> bool:
        """
        Removes a string from the trie by marking the end node as non-terminal
        (is_end = False). It does not remove the nodes themselves, because they
        may be shared with other words/phrases.

        :param trie: The trie to remove the string from.
        :param string: The string to remove.
        :return: True if the string was removed, False if the string was not
                 found.
        """
        node = trie.root
        stack = []  # To keep track of the path

        # Traverse the trie to find the string
        for char in string:
            if char not in node.children:
                return False  # String not found in trie
            stack.append((node, char))  # Store the parent node and char
            node = node.children[char]

        # Check if we reached the end of a valid word/phrase
        if node.is_end:
            # Mark the node as non-terminal
            node.is_end = False
            node.style_info = None  # Optionally clear style information

            # Clean up unused nodes if they are not part of other words/phrases
            self._cleanup_trie(stack)

            return True
        return False  # String was not found as a complete word/phrase


    @staticmethod
    def _cleanup_trie(stack: List[Tuple[Any, str]]) -> None:
        """
        Recursively clean up the trie by removing nodes that are no longer part
        of any valid words/phrases.

        :param stack: A list of (node, char) pairs that represent the path of
                      the string in the trie.
        """
        while stack:
            node, char = stack.pop()
            child_node = node.children[char]

            # If the child node has no children and is not the end of another
            # word/phrase, remove it.
            if not child_node.children and not child_node.is_end:
                del node.children[char]
            else:
                # If the child node has children or marks the end of another
                # word/phrase, stop cleaning.
                break


    def _remove_word(self, word: str) -> bool:
        """
        Removes a word from the word map.

        :param word: The word to remove.
        :return: True if the word was removed, False otherwise.
        """
        if word in self.word_map:
            del self.word_map[word]
            return True
        return False



    def search_phrases(self, text_segment: str, normalize=False, normalize_sep=' '):
        return self.phrase_trie.search_longest_prefix(text_segment, normalize, normalize_sep)

    def search_words(self, word: str):
        if self.enable_word_trie:
            word_match = self.word_trie.search(word)
            return word_match
        elif self.enable_word_map:
            return self.word_map.get(word)
        else:
            return None

    def search_subwords(self, word: str):
        # Implement subword search logic as needed
        pass


