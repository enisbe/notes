import pypandoc
from bs4 import BeautifulSoup, NavigableString, Tag
from collections import OrderedDict
import re

from time import sleep
import vertexai
from vertexai.language_models import TextGenerationModel
import os

parameters = {
"max_output_tokens": 2000,
"temperature": 0.2,
"top_p": 0.8,
"top_k": 40
}


# Set the GOOGLE_APPLICATION_CREDENTIALS environment variable to the path of the JSON key file.
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./llm-sa2.json"

PROJECT_ID = "llm-project-401322"
LOCATION = "us-central1"
vertexai.init(project=PROJECT_ID, location=LOCATION)

chat_model = TextGenerationModel.from_pretrained("text-bison")

class ContentObject:
    def __init__(self, header, content, request_id):
        self.header = header
        self.content = content
        self.request_id = request_id

    def __repr__(self):
        return f"<ContentObject(header={self.header}, content={self.content}, request_id={self.request_id})>"



def read_file(path):
    with open(path, 'r', encoding='utf-8') as file:
        doc = file.read()
    return doc

def parse_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    doc = OrderedDict()
    stack = [doc]
    for element in soup.children:
        if isinstance(element, (NavigableString, Tag)):
            parse_element(element, stack)

    return doc

def parse_element(element, stack):
    if element.name and element.name.startswith('h') and element.name[1].isdigit():

        cls = element.get('class', [])
        has_href = element.find('a', href=True)
         
        if cls:
            if (cls[0].startswith('toc-')): #  or element.find('a', href=True)):
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

# Functions to process ordered dict with LLMs. We iterate over keys and pass the argument for 
 
def convert_to_markdown(content):
    content = BeautifulSoup(content, 'html.parser')
    for p in content.find_all('p'):
        p.string = p.get_text(strip=True).replace('\n', ' ')        
    return pypandoc.convert_text(content, "markdown", format='html', extra_args=['--wrap=none'])  # This is just an example. It converts the content to uppercase.

def convert_to_html(content):
    return pypandoc.convert_text(content, "html", format='markdown', extra_args=['--wrap=none'])  # This is just an example. It converts the content to uppercase.


def llm_summary(content): 
 
    if content in ['\r\n', "\n"]:
        return content
    else:
        # return 
        response = chat_model.predict(
            f"""Provide detailed summary of the following text:\n{content}\n."""
             , **parameters
             
            )
        return response.text

def text_processing(text):
    # Example processing function. Modify this as per your requirement.
    text_md = convert_to_markdown(text)
    text_llm = llm_summary(text_md)
    text_html = convert_to_html(text_llm)  
    return text_html
 
def text_processing2(request):
    # Process the text.
    text_md = convert_to_markdown(request.content)
    text_llm = llm_summary(text_md)
    text_html = convert_to_html(text_llm)  
    
    # Return a new ContentObject with the processed text.
    return ContentObject(request.header, text_html, request.request_id)
 
def process_content(doc, func, key=''):   
    """Iterate over key element and apply func to key 'content'"""
    # If a key is provided, make it the top of the document hierarchy
    if key:
        new_doc = OrderedDict({key: OrderedDict()})
        new_doc[key] = _process_content_inner(doc, func)
        return new_doc
    else:
        return _process_content_inner(doc, func)

def _process_content_inner(doc, func):   
    """Inner recursive function to iterate over key element and apply func to key 'content'."""
    # If the doc is a dictionary, iterate over its items
    if isinstance(doc, dict):
        new_doc = OrderedDict()
        for k, value in doc.items():
            if k == 'content':
                # Apply the transformation function to the 'content' and store it in the new_doc
                new_doc[k] = func(value)
            else:
                # For non-content items, continue the recursive copying process
                new_doc[k] = _process_content_inner(value, func)
        return new_doc
    else:
        # If the doc is not a dictionary (i.e., it's a string content but not under the 'content' key), just return it as is
        return doc

def reconstruct_html(section_header, doc, indent_level=0):
    """ Reconstruct html from any key"""
    
    html = f"{'  ' * indent_level}{section_header}\n"
    
    for key, value in doc.items():
        if key == 'content':
            # Adding content
            html += f"{'  ' * (indent_level+1)}{value}\n"
        else:
            # Adding headers and recursively adding sub-headers/content
            html += reconstruct_html(key, value, indent_level+1)    
    return html


# def process_content_stream(doc, func, q, key=''): # works but it does output the right document which is fine b/c it is printing only. But i Rather fix this with the process below
#     """Iterate over key element, apply func to key 'content', and stream the processed content to the queue."""
#     # If the doc is a dictionary, iterate over its items

#     # If a key is provided, put it into the queue
#     if key:
#         q.put(key)

    
#     if isinstance(doc, dict):
#         new_doc = OrderedDict()
#         for key, value in doc.items():
#             if key == 'content':
#                 # Apply the transformation function to the 'content' and store it in the new_doc
#                 new_doc[key] = func(value)
#                 q.put(new_doc[key])  # Put the processed content in the queue
#             else:
#                 q.put(key)
#                 # For non-content items, continue the recursive copying process
#                 new_doc[key] = process_content_stream(value, func, q)
#         return new_doc


def process_content_stream(doc, func, q, key=''):
    """Iterate over key element, apply func to key 'content', and stream the processed content to the queue."""
    
    if key:
        q.put(key)
        new_doc = OrderedDict({key: _process_content_stream_inner(doc, func, q)})
        return new_doc
    else:
        return _process_content_stream_inner(doc, func, q)

def _process_content_stream_inner(doc, func, q):
    if isinstance(doc, dict):
        new_inner_doc = OrderedDict()
        for k, value in doc.items():
            if k == 'content':
                # Apply the transformation function to the 'content' and store it in the new_inner_doc
                new_inner_doc[k] = func(value)
                q.put(new_inner_doc[k])  # Put the processed content in the queue
            else:
                q.put(k)
                new_inner_doc[k] = _process_content_stream_inner(value, func, q)
        return new_inner_doc


# # Using a global counter for the request ID.
# global_request_id = 1

def process_content_request(doc, key=''):   
    """Iterate over key element and generate ContentObjects."""
    # Resetting the global_request_id each time the process_content is called
    global global_request_id
    global_request_id = 1
    
    processed_list = []
    _process_content__request_inner(doc, processed_list)
    return processed_list

def _process_content__request_inner(doc, processed_list):   
    """Inner recursive function to iterate over key element and generate ContentObjects."""
    global global_request_id

    # If the doc is a dictionary, iterate over its items
    if isinstance(doc, dict):
        for k, value in doc.items():
            if k.startswith('<h'):
                # Assign a new request ID for the header
                current_request_id = global_request_id
                global_request_id += 1
                
                # Process inner content for this header
                if 'content' in value:
                    content_obj = ContentObject(k, value['content'], current_request_id)
                    processed_list.append(content_obj)

                # Recursively process inner elements
                _process_content__request_inner(value, processed_list)
    return processed_list 

