# html_processor.py

from collections import OrderedDict
from bs4 import BeautifulSoup, NavigableString, Tag

class HTMLProcessor:
    
    def __init__(self):
        self.doc = OrderedDict()

    def parse_html(self, html: str) -> OrderedDict:
        """
        Parses an HTML string into an ordered dictionary representation.
        
        Args:
        - html (str): The HTML string to be parsed.

        Returns:
        - OrderedDict: The parsed HTML representation.
        """
        soup = BeautifulSoup(html, 'html.parser')
        stack = [self.doc]
        for element in soup.children:
            if isinstance(element, (NavigableString, Tag)):
                self.parse_element(element, stack)
        return self.doc

    def parse_element(self, element, stack: list):
        """
        Parses a BeautifulSoup element and updates the stack accordingly.

        Args:
        - element: The BeautifulSoup element to be parsed.
        - stack (list): A list representing the current hierarchy of elements.
        """
        if element.name and element.name.startswith('h') and element.name[1].isdigit():
            cls = element.get('class', [])
            has_href = element.find('a', href=True)
             
            if cls:
                if (cls[0].startswith('toc-')):
                    return

            # Determine the level of the header
            level = int(element.name[1]) - 1

            # Ensure that the stack is deep enough for the header level
            while len(stack) <= level:
                new_dict = OrderedDict()
                stack[-1][str(element)] = new_dict
                stack.append(new_dict)

            # If we are backtracking, e.g., from <h3> to <h2>, remove unnecessary deeper levels from the stack
            while len(stack) > level + 1:
                stack.pop()

            # Add a new OrderedDict for the header and set the pointer there
            new_dict = OrderedDict()
            stack[level][str(element)] = new_dict
            if len(stack) == level + 1:
                stack.append(new_dict)

        else:
            # If we have content, add it to the current deepest level
            if len(stack) > 1:
                if 'content' not in stack[-1]:
                    stack[-1]['content'] = ""
                stack[-1]['content'] += str(element)

    def reconstruct_html(self, section_header: str, doc: OrderedDict, indent_level: int = 0) -> str:
        """
        Reconstructs an HTML string from the ordered dictionary representation.

        Args:
        - section_header (str): The current section header being processed.
        - doc (OrderedDict): The ordered dictionary representation of the HTML.
        - indent_level (int): The current indentation level for formatting.

        Returns:
        - str: The reconstructed HTML string.
        """
        html = f"{'  ' * indent_level}{section_header}\n"
        
        for key, value in doc.items():
            if key == 'content':
                html += f"{'  ' * (indent_level+1)}{value}\n"
            else:
                html += self.reconstruct_html(key, value, indent_level+1)
        return html
