import threading
import queue
import time

def split_text_into_chunks(text, chunk_size=5):
    """Split the input text into fixed-size chunks."""
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]



def display_text(rightpane, text, delay=0.005):
    # Reset the current state
    index = 0
    text_chunks = split_text_into_chunks(text)
    # Using a while loop to print each chunk with a delay
    while index < len(text_chunks):
        new_content = rightpane.object + f"{text_chunks[index]}"
        rightpane.object = new_content         
        index += 1
        time.sleep(delay)
        

def print_content(q, pane):
    while True:
        # Check if there's content in the queue
        try:
            content = q.get(timeout=1)
            
            # new_content = pane.object + content 
            # pane.object =  new_content

            display_text(pane, content, delay=0.005)
             
        except queue.Empty:
            time.sleep(1)

