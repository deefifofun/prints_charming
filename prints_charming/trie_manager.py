# trie_manager.py

import re



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
        node.insertion_order = self.insertion_counter  # Set the insertion order
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
            text = re.sub(r'\s+', normalize_sep, text)  # Normalize spaces

        node = self.root
        longest_match = None
        current_match = []
        match_length_original = 0  # Track the length of the match to map back to original text

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
            original_match = original_text[:match_length_original]  # Extract original matched text
            return original_match, longest_match[1]  # Return original match with style info


        """
        node = self.root
        longest_match = None
        current_match = []
        for char in text:
            if char not in node.children:
                break
            node = node.children[char]
            current_match.append(char)
            if node.is_end:
                longest_match = (''.join(current_match), node.style_info)
        return longest_match
        """

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
        # Sort matches by the insertion order to prioritize the earliest added substring
        matches.sort(key=lambda x: x[2])  # Sort by insertion_order
        return matches if matches else None


    def search(self, text):
        node = self.root
        for char in text:
            if char not in node.children:
                return None  # Phrase not found
            node = node.children[char]
        return node.style_info if node.is_end else None


