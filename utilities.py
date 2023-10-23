# utilities.py

import pypandoc
from bs4 import BeautifulSoup

def read_file(path: str) -> str:
    """
    Reads the content of a file given its path.
    
    Args:
    - path (str): The path to the file.

    Returns:
    - str: The content of the file.
    """
    with open(path, 'r', encoding='utf-8') as file:
        return file.read()

def convert_to_markdown(content: str) -> str:
    """
    Converts the given HTML content to Markdown format.

    Args:
    - content (str): The HTML content to be converted.

    Returns:
    - str: The content in Markdown format.
    """
    content_soup = BeautifulSoup(content, 'html.parser')
    for p in content_soup.find_all('p'):
        p.string = p.get_text(strip=True).replace('\n', ' ')
        
    return pypandoc.convert_text(content_soup, "markdown", format='html', extra_args=['--wrap=none'])

def convert_to_html(content: str) -> str:
    """
    Converts the given Markdown content to HTML format.

    Args:
    - content (str): The Markdown content to be converted.

    Returns:
    - str: The content in HTML format.
    """
    return pypandoc.convert_text(content, "html", format='markdown', extra_args=['--wrap=none'])
