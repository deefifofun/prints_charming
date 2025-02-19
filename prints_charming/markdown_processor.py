import sys
import re
from typing import Any, List, LiteralString, Tuple, Union


class MarkdownProcessor:
    def __init__(self, pc_instance):
        """
        Initialize the MarkdownProcessor with a reference to the PrintsCharming instance.

        :param pc_instance: An instance of the PrintsCharming class.
        """
        self.pc = pc_instance
        self.markdown_pattern = re.compile(
            r"```(\w*)\n([\s\S]*?)```"  # group(1)->language, group(2)->code block
            r"|^(#+)\s+(.+)"  # group(3)->header symbols, group(4)->header text
            r"|\*\*(.+?)\*\*"  # group(5)->bold text
            r"|\*(.+?)\*"  # group(6)->italic text
            r"|-\s+(.+)"  # group(7)->list item
            r"|\[(.+?)\]\((.+?)\)"  # group(8)->link text, group(9)->link URL
            r"|`([^`]+)`",  # group(10)->inline code
            re.MULTILINE
        )


    def apply_custom_python_highlighting(self, code_block):
        reset_code = self.pc.RESET
        ansi_sgr_loose_pattern = self.pc.ansi_escape_patterns['sgr_loose']

        # Simple regex patterns for Python elements
        builtin_pattern = r'\b(print|input|len|range|map|filter|open|help)\b'
        keyword_pattern = r'\b(def|return|class|if|else|elif|for|while|import|from|as|in|try|except|finally|not|and|or|is|with|lambda|yield)\b'
        string_pattern = r'(\".*?\"|\'.*?\')'
        comment_pattern = r'(#.*?$)'
        variable_pattern = r'(\b\w+)\s*(=)'  # Capture variables being assigned and preserve spaces
        fstring_pattern = r'\{(\w+)\}'
        number_pattern = r'(?<!\033\[|\d;)\b\d+(\.\d+)?\b'  # Exclude sequences like 5 in "38;5;248m"

        # Pattern for matching function signatures
        function_pattern = r'(\b\w+)(\()([^\)]*)(\))(\s*:)'
        function_call_pattern = r'(\b\w+)(\()([^\)]*)(\))'  # Function calls without a trailing colon
        #param_pattern = r'(\w+)(\s*=\s*)(\w+)?'  # For parameters with default values
        param_pattern = r'(\w+)(\s*=\s*)([^\),]+)'  # This pattern captures the parameters and their default values
        cls_param_pattern = r'\bcls\b'   # For detecting 'cls' parameter
        self_param_pattern = r'\bself\b'  # For detecting 'self' parameter

        # Exclude ANSI escape sequences from number styling
        code_block = ansi_sgr_loose_pattern.sub(lambda match: match.group(0), code_block)

        # Apply styles to comments, strings, builtins, keywords
        code_block = re.sub(comment_pattern, f'{self.pc.style_codes.get('python_comment', '')}\\g<0>{reset_code}', code_block, flags=re.MULTILINE)
        code_block = re.sub(string_pattern, f'{self.pc.style_codes.get('python_string', '')}\\g<0>{reset_code}', code_block)
        code_block = re.sub(builtin_pattern, f'{self.pc.style_codes.get('python_builtin', '')}\\g<0>{reset_code}', code_block)
        code_block = re.sub(keyword_pattern, f'{self.pc.style_codes.get('python_keyword', '')}\\g<0>{reset_code}', code_block)

        # Now apply number styling to numbers that are not part of ANSI sequences
        code_block = re.sub(number_pattern, f'{self.pc.style_codes.get('python_number', '')}\\g<0>{reset_code}', code_block)

        # Apply styles to variables
        code_block = re.sub(variable_pattern, f'{self.pc.style_codes.get('python_variable', '')}\\1{reset_code} \\2', code_block)

        # Apply f-string variable styling inside curly braces
        code_block = re.sub(fstring_pattern, f'{self.pc.style_codes.get('python_fstring_variable', '')}{{\\1}}{reset_code}', code_block)


        def param_replacer(param_match):
            param_name = ansi_sgr_loose_pattern.sub('', param_match.group(1))  # Exclude ANSI sequences

            equal_sign = param_match.group(2).strip()
            default_value = param_match.group(3)

            styled_param_name = f'{self.pc.style_codes["python_param"]}{param_name}{reset_code}'
            styled_equal_sign = f'{self.pc.style_codes["python_operator"]}{equal_sign}{reset_code}'
            styled_default_value = f'{self.pc.style_codes["python_default_value"]}{default_value}{reset_code}'
            params = f'{styled_param_name}{styled_equal_sign}{styled_default_value}'

            return params

        # Match function signatures and apply styles to different parts
        def function_replacer(match):
            function_name = ansi_sgr_loose_pattern.sub('', match.group(1))  # Function name
            parenthesis_open = ansi_sgr_loose_pattern.sub('', match.group(2))
            params = ansi_sgr_loose_pattern.sub('', match.group(3))  # Parameters
            parenthesis_close = ansi_sgr_loose_pattern.sub('', match.group(4))
            colon = match.group(5) if len(match.groups()) == 5 else ''

            # Apply styles and reset codes
            styled_function_name = f'{self.pc.style_codes["python_function_name"]}{function_name}{reset_code}'
            styled_parenthesis_open = f'{self.pc.style_codes["python_parenthesis"]}{parenthesis_open}{reset_code}'
            styled_params = re.sub(cls_param_pattern, f'{self.pc.style_codes["python_self_param"]}cls{reset_code}', params)
            styled_params = re.sub(self_param_pattern, f'{self.pc.style_codes["python_self_param"]}self{reset_code}', styled_params)
            styled_params = re.sub(param_pattern, param_replacer, styled_params)
            styled_parenthesis_close = f'{self.pc.style_codes["python_parenthesis"]}{parenthesis_close}{reset_code}'
            styled_colon = f'{self.pc.style_codes["python_colon"]}{colon}{reset_code}'

            function_sig = f'{styled_function_name}{styled_parenthesis_open}{styled_params}{styled_parenthesis_close}{styled_colon}'

            self.pc.debug(f'{function_sig}')

            return function_sig


        # Apply the function_replacer for function signatures
        code_block = re.sub(function_pattern, function_replacer, code_block)
        self.pc.debug(f'\n\n{code_block}\n')

        # Match and style function calls (function calls don't have trailing colons)
        def function_call_replacer(match):
            #function_name = f'{function_name_style_code}{match.group(1)}{reset_code}'  # Function name in calls
            function_name = ansi_sgr_loose_pattern.sub('', match.group(1))  # Function name
            #parenthesis_open = f'{parenthesis_style_code}{match.group(2)}{reset_code}'
            parenthesis_open = ansi_sgr_loose_pattern.sub('', match.group(2))
            #params = match.group(3)
            params = ansi_sgr_loose_pattern.sub('', match.group(3))  # Exclude ANSI sequences
            #parenthesis_close = f'{parenthesis_style_code}{match.group(4)}{reset_code}'
            parenthesis_close = ansi_sgr_loose_pattern.sub('', match.group(4))

            # Apply styles to 'cls' parameter within function calls
            styled_params = re.sub(cls_param_pattern, f'{self.pc.style_codes.get('python_self_param', '')}cls{reset_code}', params)

            # Apply styles to 'self' parameter within function calls
            styled_params = re.sub(self_param_pattern, f'{self.pc.style_codes.get('python_self_param', '')}self{reset_code}', params)

            # Apply styles to parameters with default values
            styled_params = re.sub(param_pattern, param_replacer, styled_params)

            styled_function_call = f'{function_name}{parenthesis_open}{styled_params}{parenthesis_close}'

            return styled_function_call

        # Apply the function_call_replacer for function calls
        code_block = re.sub(function_call_pattern, function_call_replacer, code_block)
        self.pc.debug(f'\n\n{code_block}\n')

        return code_block

    def apply_markdown_style(
            self,
            style_name: str,
            content: Any,
            reset: bool = True
    ) -> str:
        """
        Apply the style corresponding to style_name to 'content'.
        'nested_styles' can override or provide finer-grained styling for sub-parts.
        """
        reset_code = self.pc.reset if reset else ''

        if style_name != 'link':
            style_code = self.pc.style_codes.get(style_name, self.pc.color_map.get(style_name, self.pc.color_map.get('default')))

            # Handle code block separately for better readability
            if style_name == 'code_block':
                language = content.split("\n", 1)[0]  # Get the first line, which is the language identifier (e.g., 'python')
                code = content[len(language):]  # The rest is the actual code block content
                highlighted_code = self.apply_custom_python_highlighting(code.strip())
                # Combine the language identifier with the highlighted code block
                styled_text = f"{style_code}{language}{reset_code}\n{highlighted_code}"
            else:
                # Apply the style and reset code for other markdown types
                styled_text = f"{style_code}{content}{reset_code}"

            return styled_text

        else:
            """
            'content' here is (link_text, link_url).
            We can apply distinct styles for each part.
            """
            if isinstance(content, tuple):
                link_text, link_url = content

                link_text_code = self.pc.style_codes.get('link_text', "")
                link_url_code = self.pc.style_codes.get('link_url', "")


                styled_link_text = f"{link_text_code}{link_text}{reset_code}"
                styled_link_url = f"{link_url_code}{link_url}{reset_code}"

                styled_full_link = (
                    f"[{styled_link_text}]"  # text portion
                    f"({styled_link_url})"  # url portion
                )
            else:
                content_code = self.pc.style_codes.get('link_url', '')
                styled_full_link = f"{content_code}{content}{reset_code}"

            return styled_full_link




    def apply_markdown_style2(self, style_name, text, nested_styles=None, reset=True):
        text = str(text)
        print(f"Initial input text as string: {text}")

        if nested_styles:
            # If nested_styles is a dictionary, process specific parts separately
            print(f"Nested styles provided: {nested_styles}")

            def style_link_parts(match):
                styled_text = match.group(0)  # Default is the full match (e.g., `[text](url)`)

                if match.group(8) and match.group(9):  # If it's a link
                    link_text = match.group(8)  # Extract the link text
                    link_url = match.group(9)  # Extract the link URL

                    # Apply separate styles if defined
                    styled_link_text = self.apply_markdown_style(nested_styles.get('link_text', ''), link_text)
                    styled_link_url = self.apply_markdown_style(nested_styles.get('link_url', ''), link_url)

                    # Reconstruct the link with styles
                    styled_text = f"[{styled_link_text}]({styled_link_url})"

                    print(f'\n\n\n\n\n\n\n\n\n\n\n\n\n\n\nPRINTING STYLED TEXT!!!!!!!!!!!!!!!!!!!!!!!!!!!\n\n\n\n\n\n\n')
                    print(styled_text)

                return styled_text

            if isinstance(nested_styles, dict):
                # Debugging: Print the regex pattern and test it
                print(f"Markdown pattern: {self.markdown_pattern.pattern}")
                print(f"Regex matches: {re.findall(self.markdown_pattern, text)}")

                for match in self.markdown_pattern.finditer(text):
                    print(f"Match groups: {match.groups()}")

                print("Applying markdown pattern substitution...")

                # Apply nested styles using the markdown pattern
                text = self.markdown_pattern.sub(style_link_parts, text)

            # Handle simple nested styles (list)
            elif isinstance(nested_styles, list):
                for nested_style in nested_styles:
                    text = self.apply_markdown_style(nested_style, text, reset=False)

        else:
            print(f"Nested styles NOT provided: {nested_styles}")

        # Fetch the corresponding style code
        style_code = self.pc.style_codes.get(style_name, self.pc.color_map.get(style_name, self.pc.color_map.get('default')))

        # Apply reset code carefully for nested styles
        reset_code = self.pc.reset if reset else ''

        # Handle code block separately for better readability
        if style_name == 'code_block':
            language = text.split("\n", 1)[0]  # Get the first line, which is the language identifier (e.g., 'python')
            code = text[len(language):]  # The rest is the actual code block content
            highlighted_code = self.apply_custom_python_highlighting(code.strip())
            # Combine the language identifier with the highlighted code block
            styled_text = f"{style_code}{language}{reset_code}\n{highlighted_code}"
        else:
            # Apply the style and reset code for other markdown types
            styled_text = f"{style_code}{text}{reset_code}"

        return styled_text



    def parse_markdown(self, text: str, idx: int = 0) -> list[tuple[str, str] | tuple[str, LiteralString] | tuple[str, list[tuple[str, str]]]]:

        parsed_segments = []
        pos = 0

        # Use the precompiled pattern
        for match in self.markdown_pattern.finditer(text):
            start, end = match.span()

            # 1) Add unmatched text before this match
            if start > pos:
                unmatched_text = text[pos:start]
                # Only add it if it's not empty (or you can always add it, if you prefer)
                if unmatched_text:
                    #print(f'unmatched text idx({idx}): True')
                    invisible_text = None
                    if '\n' in unmatched_text or '\t' in unmatched_text:
                        unmatched_text = unmatched_text.rstrip('!')
                        invisible_text = unmatched_text.replace('\n', '\\n').replace('\t', '\\t')
                    if not invisible_text:
                        pass
                        #print(f'unmatched_text contents idx({idx}): {unmatched_text}')
                    else:
                        pass
                        #print(f'unmatched_text contents idx({idx}): {invisible_text}')
                    parsed_segments.append(('default', unmatched_text))

            # 2) Figure out which group is matched
            if match.group(1) is not None:
                #print(f'group1 match idx({idx}): True')
                # code block
                language = match.group(1) or 'default'
                code_block = match.group(2).rstrip()
                # Normalize indentation here if you want
                lines = code_block.split('\n')
                min_indent = min(
                    (len(line) - len(line.lstrip())
                     for line in lines if line.strip()),
                    default=0
                )
                normalized_code_block = "\n".join(line[min_indent:] for line in lines)
                parsed_segments.append(('code_block', f"{language}\n{normalized_code_block}"))


            elif match.group(3) is not None:
                #print(f'group3 match idx({idx}): True')
                # header
                header_level = len(match.group(3))
                header_content = match.group(4).strip()
                parsed_segments.append((f'header{header_level}', header_content))

            elif match.group(5) is not None:
                #print(f'group5 match idx({idx}): True')
                # bold
                parsed_segments.append(('bold', match.group(5).strip()))

            elif match.group(6) is not None:
                #print(f'group6 match idx({idx}): True')
                # italic
                parsed_segments.append(('italic', match.group(6).strip()))

            elif match.group(7) is not None:
                #print(f'group7 match idx({idx}): True')
                # list item
                #parsed_segments.append(('bullet', match.group(7).strip()))
                # The bullet text without the leading '-' is match.group(7)
                bullet_text = match.group(7).strip()

                # Recursively parse the bullet text so we can detect **bold**, *italic*, etc.
                sub_segments = self.parse_markdown(bullet_text)

                # We'll store this as a special type that indicates a "bullet" containing
                # nested segments. This is different from simply ('bullet', string).
                # Instead, it's ('bullet', [ (sub_style, sub_content), ... ]).
                parsed_segments.append(('bullet', sub_segments))


            elif match.group(8) is not None:
                #print(f'group8 match idx({idx}): True')
                link_text = match.group(8).strip()
                link_url = match.group(9).strip()
                #print(f'link_text idx({idx}): {link_text}, link_url idx({idx}): {link_url}\n\n\n\n')
                #parsed_segments.append(('link', f"{link_text} ({link_url})"))
                parsed_segments.append(('link', (link_text, link_url)))


            elif match.group(10) is not None:
                #print(f'group10 match idx({idx}): True')
                # inline code
                parsed_segments.append(('inline_code', match.group(10).strip()))

            pos = end

            # 3) Finally, capture any remaining text after the last match
        if pos < len(text):
            unmatched_text = text[pos:]
            if unmatched_text:
                #print(f'unmatched text remaining idx({idx}): True')
                invisible_text = None
                if '\n' in unmatched_text or '\t' in unmatched_text:
                    unmatched_text = unmatched_text.rstrip('!')
                    invisible_text = unmatched_text.replace('\n', '\\n').replace('\t', '\\t')
                if not invisible_text:
                    pass
                    #print(f'unmatched_text remaining contents idx({idx}): {unmatched_text}')
                else:
                    pass
                    #print(f'unmatched_text remaining contents idx({idx}): {invisible_text}')
                parsed_segments.append(('default', unmatched_text))

        """
        print(f'parsed_segments:')
        for i, segment in enumerate(parsed_segments):
            print(f'parsed_segment({i}): {segment}')
        print(f'\n\n\n\n\n\n\n')
        """

        return parsed_segments



    def print(self,
              *args: Any,
              sep: str = '',
              end: str = '\n',
              indent: int = 0,
              tab_width: int = 4,
              container_width: Union[int, None] = None,
              prepend_fill: bool = False,
              fill_to_end: bool = False,
              fill_with: str = ' ',
              preserve_newlines: bool = True,
              filename: str = None,
              **kwargs) -> None:
        """
        Higher-level method to parse Markdown, apply styles, wrap lines, and output.
        """

        if not container_width:
            container_width = self.pc.terminal_width

        converted_args = [str(arg) for arg in args]
        markdown_segments = []
        # Parse each argument into style segments
        for i, arg in enumerate(converted_args):
            markdown_segments.extend(self.parse_markdown(arg, idx=i))

        # Build a single styled string from the segments
        styled_output_parts = []
        for style_name, content in markdown_segments:
            if style_name == 'bullet':
                # 'content' is a list of sub-segments
                bullet_sub_styles = []
                for (sub_style, sub_text) in content:
                    bullet_sub_styles.append(self.apply_markdown_style(sub_style, sub_text))
                # Combine sub-parts, then prepend bullet symbol
                bullet_line = ''.join(bullet_sub_styles)
                bullet_line = f"● {bullet_line}"
                # Optionally indent bullets
                bullet_line = self.apply_markdown_style('bullet', bullet_line)
                bullet_line = f"\t{bullet_line}"
                styled_output_parts.append(bullet_line)
            else:
                styled_part = self.apply_markdown_style(style_name, content)
                styled_output_parts.append(styled_part)

        #print(f'\n\n\nstyled_output_parts:')
        #for i, styled_output_part in enumerate(styled_output_parts):
            #print(f'styled_output_part({i}):', repr(styled_output_part))
        #print(f'\n\n\n\n\n')

        # Join them into one big chunk to be wrapped
        full_styled_text = sep.join(styled_output_parts)

        #print(f'full_styled_text_repr:')
        #print(repr(full_styled_text))
        #print(f'\n\n\n')

        #sys.stdout.write(f'full_styled_text:\n{full_styled_text}\n\n\n\n')

        #print(f'full_styled_text:\n{full_styled_text}\n\n\n\n')

        # Wrap text (ANSI-aware) - no bullet logic inside wrap_text
        wrapped_lines = self.pc.wrap_text_ansi_aware(
            full_styled_text,
            width=container_width,
            indent=indent,
            tab_width=tab_width,
            prepend_fill=prepend_fill,
            fill_to_end=fill_to_end,
            fill_char=fill_with,
            preserve_newlines=preserve_newlines
        )

        #print(f'wrapped_lines:\n{wrapped_lines}')

        final_output = ''.join(wrapped_lines)
        if filename:
            with open(filename, 'a') as f:
                f.write(final_output + end)
        else:
            sys.stdout.write(final_output + end)
            #self.pc.print(final_output, end=end, skip_ansi_check=True)
            #print(final_output, end=end)





    def print_markdown_orig(
            self,
            *args: Any,
            sep: str = ' ',
            end: str = '\n',
            indent: int = 0,
            tab_width: int = 4,
            container_width: Union[int, None] = None,
            prepend_fill: bool = False,
            fill_to_end: bool = False,
            fill_with: str = ' ',
            filename: str = None,
            **kwargs
    ) -> None:


        if not container_width:
            container_width = self.pc.terminal_width

        converted_args = [str(arg) for arg in args]

        markdown_segments = []
        for arg in converted_args:
            markdown_segments.extend(self.parse_markdown(arg))

        styled_output = []

        for style_name, content in markdown_segments:
            print(f"style_name: {style_name}\ncontent: {content}")
            # Only skip empty strings for non-plain text.
            # But if content is a list (bullet), skip this check or handle differently.
            if isinstance(content, str):
                if not content.strip() and style_name != 'default':
                    continue
            else:
                # Here, `content` is a list (like for bullet sub-segments).
                # If you want to skip truly empty bullet lines:
                if not content:  # e.g. empty list
                    continue

            if style_name == 'header1':
                styled_output.append(self.apply_markdown_style('header1', content))
            elif style_name == 'header2':
                styled_output.append(self.apply_markdown_style('header2', content))
            elif style_name == 'header3':
                styled_output.append(self.apply_markdown_style('header3', content))
            elif style_name == 'bold':
                styled_output.append(self.apply_markdown_style('bold', content))
            elif style_name == 'italic':
                styled_output.append(self.apply_markdown_style('italic', content))
            elif style_name == 'bullet':
                # content is now a list of sub-segments for that bullet line
                bullet_sub_segments = content

                # We’ll manually build a new string by rendering each sub-segment
                # in the bullet line, so that bold text gets the bullet_title style, etc.
                sub_styled_parts = []
                for (sub_style_name, sub_text) in bullet_sub_segments:
                    if sub_style_name == 'bold':
                        sub_styled_parts.append(self.apply_markdown_style('bullet_title', sub_text))
                    elif sub_style_name == 'italic':
                        sub_styled_parts.append(self.apply_markdown_style('italic', sub_text))
                    elif sub_style_name == 'link':
                        sub_styled_parts.append(self.apply_markdown_style('link', sub_text))
                    elif sub_style_name == 'inline_code':
                        sub_styled_parts.append(self.apply_markdown_style('inline_code', sub_text))
                    # ... handle all possible sub-styles, including nested bullets, etc.
                    else:
                        # Treat everything else as plain text
                        sub_styled_parts.append(sub_text)

                # Now we join those sub-styled parts together into a single line
                bullet_line = ''.join(sub_styled_parts)

                # Finally, we apply the bullet style *and* prepend "● "
                # to the line as a whole. That way we keep a consistent bullet style.
                bullet_styled = self.apply_markdown_style('bullet', f"● {bullet_line}")

                # Prepend a tab
                bullet_styled = f"\t{bullet_styled}"

                styled_output.append(bullet_styled)
            elif style_name == 'link':
                styled_output.append(self.apply_markdown_style('link', content))
            elif style_name == 'inline_code':
                styled_output.append(self.apply_markdown_style('inline_code', content))
            elif style_name == 'code_block':  # Ensure code block is styled and printed
                styled_output.append(self.apply_markdown_style('code_block', content))
            elif style_name == 'plain':
                styled_output.append(content)

        # Join the styled output and proceed with regular printing
        joined_styled_output = sep.join(styled_output)

        print(f'JOINED STYLED OUTPUT!!!!!!:\n{joined_styled_output}')

        #wrapped_styled_lines = self.pc.wrap_styled_text(joined_styled_output, container_width, tab_width)
        wrapped_styled_lines = self.pc.wrap_text_ansi_aware(joined_styled_output,
                                                            container_width,
                                                            indent=indent,
                                                            tab_width=tab_width,
                                                            prepend_fill=prepend_fill,
                                                            fill_to_end=fill_to_end,
                                                            markdown=False)

        print(f'WRAPPED STYLED LINES!!!!!!: {wrapped_styled_lines}')

        joined_wrapped_styled_lines = sep.join(wrapped_styled_lines)

        print(f'joined_wrapped_styled_lines:\n{joined_wrapped_styled_lines}')

        final_lines = []
        for line in wrapped_styled_lines:
            # Handle prepend_fill
            if prepend_fill:
                # Replace leading newlines and tabs in 'line' with fill_with * (tab_width * n_tabs)
                line = self.pc.replace_leading_newlines_tabs(line, fill_with, tab_width)

            # Calculate the number of trailing newlines
            trailing_newlines = len(line) - len(line.rstrip('\n'))

            # Check if the line is empty (contains only a newline character)
            stripped_line = line.rstrip('\n')
            has_newline = line.endswith('\n')

            if fill_to_end:
                # Calculate the visible length of the line
                visible_line = self.pc.remove_ansi_codes(stripped_line)
                current_length = self.pc.get_visible_length(visible_line.expandtabs(tab_width), tab_width=tab_width)
                chars_needed = max(0, container_width - current_length)

                # If the line ends with the ANSI reset code, remove it temporarily
                has_reset = stripped_line.endswith(self.pc.reset)
                if has_reset:
                    stripped_line = stripped_line[:-len(self.pc.reset)]

                # Add padding characters and then the reset code if it was present
                padded_line = stripped_line + fill_with * chars_needed
                if has_reset:
                    padded_line += self.pc.reset

                # Re-append the newline character if it was present
                if trailing_newlines > 0:
                    padded_line += '\n' * trailing_newlines

                final_lines.append(padded_line)
            else:
                final_lines.append(line)


        final_all_styled_text = ''.join(final_lines)

        # Print or write to file
        if filename:
            with open(filename, 'a') as file:
                file.write(final_all_styled_text + end)
        else:
            print(final_all_styled_text, end=end)
        return












