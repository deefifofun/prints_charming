import re


"""
This module defines regex patterns for handling and processing whitespace
and text-based elements.

These patterns are designed to identify leading whitespace, individual words,
and spaces in strings. They can be utilized for precise text parsing, 
manipulation, and analysis.

Use Cases:
- Cleaning or preprocessing text data.
- Parsing and tokenizing strings for word-based or whitespace-sensitive operations.
- Enhancing the `PrintsCharming` library's text processing capabilities.
"""


LEADING_WS_PATTERN = re.compile(r'^([\n\t]+)')
"""
Matches leading whitespace consisting of newlines (`\n`) and tabs (`\t`).

Starts with:
- The beginning of the string (`^`).

Contains:
- One or more (`+`) newline or tab characters (`[\n\t]`).

**Example matches:**
- '\\n\\t\\nHello, world!' -> '\\n\\t\\n' (matches the leading whitespace).
- '\\t\\tIndented text' -> '\\t\\t'.

Use cases:
- Cleaning or trimming leading whitespace in text.
- Identifying and removing unwanted newlines or tabs at the start of strings.
"""


WORDS_AND_SPACES_PATTERN = re.compile(r'\S+|\s+')
"""
Matches sequences of words (non-whitespace characters) or spaces (whitespace 
characters).

Contains:
- `\\S+`: Matches one or more (`+`) non-whitespace characters (e.g., words).
- `\\s+`: Matches one or more (`+`) whitespace characters (e.g., spaces).

**Example matches:**
- 'Hello world!' -> ['Hello', ' ', 'world', '!'] (separate words and spaces).
- '\\tTabbed\\nText' -> ['\\t', 'Tabbed', '\\n', 'Text'].

Use cases:
- Tokenizing text into words and spaces for processing or styling.
- Parsing strings where words and spaces need to be treated as separate tokens.
"""
