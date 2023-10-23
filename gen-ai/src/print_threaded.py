import threading
import queue
import time
from typing import List, Union

class Pane:
    """
    An example Pane class to represent the pane object used in the display_text function.
    This is a stub and may need to be replaced with the actual Pane implementation.
    """
    def __init__(self):
        self.object = ""

def split_text_into_chunks(text: str, chunk_size: int = 5) -> List[str]:
    """
    Splits the input text into fixed-size chunks.

    Args:
    - text (str): The input text to be split.
    - chunk_size (int, optional): The size of each chunk. Defaults to 5.

    Returns:
    - List[str]: A list containing the chunks of the input text.
    """
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

def display_text(rightpane: Pane, text: str, delay: float = 0.005) -> None:
    """
    Displays the input text in the right pane by printing each chunk with a delay.

    Args:
    - rightpane (Pane): The pane object where the text will be displayed.
    - text (str): The input text to be displayed.
    - delay (float, optional): The time delay (in seconds) between displaying each chunk. Defaults to 0.005 seconds.

    Returns:
    - None
    """
    # Split the text into chunks
    text_chunks = split_text_into_chunks(text)
    
    # Iterate through the chunks and display them with a delay
    for chunk in text_chunks:
        new_content = rightpane.object + chunk
        rightpane.object = new_content
        time.sleep(delay)

def print_content(q: queue.Queue, pane: Pane) -> None:
    """
    Continuously checks and prints content from a queue in a pane. If there's no content available, 
    the function waits for a second and then re-checks.

    Args:
    - q (queue.Queue): The queue object containing the content to be printed.
    - pane (Pane): The pane object where the content will be displayed.

    Returns:
    - None
    """
    while True:
        try:
            content = q.get(timeout=1)  # Wait for content for up to 1 second
            display_text(pane, content, delay=0.005)  # Display the retrieved content
        except queue.Empty:
            # If the queue is empty, wait for 1 second before checking again
            time.sleep(1)