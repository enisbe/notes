import math
from google.cloud import documentai_v1 as documentai
from PIL import Image, ImageDraw

# Assuming you have Document AI client and have sent a request
client = documentai.DocumentProcessorServiceClient()
# Replace 'project-id', 'location-id', 'processor-id', 'file-path' with your actual values
request = documentai.ProcessRequest(name='projects/project-id/locations/location-id/processors/processor-id', document=documentai.Document(input_config=documentai.Document.InputConfig(gcs_document={'uri': 'file-path'})))
result = client.process_document(request=request)

# Your target box definition
target_box = [
    {'x': 0.1, 'y': 0.1},  # Top-left vertex
    {'x': 0.1, 'y': 0.2},  # Bottom-left vertex
    {'x': 0.2, 'y': 0.2},  # Bottom-right vertex
    {'x': 0.2, 'y': 0.1}   # Top-right vertex
]

def find_closest_box(target_box, boxes):
    target_centroid = ((target_box[0]['x'] + target_box[2]['x']) / 2, (target_box[0]['y'] + target_box[2]['y']) / 2)
    target_area = (target_box[2]['x'] - target_box[0]['x']) * (target_box[2]['y'] - target_box[0]['y'])

    closest_box = None
    closest_distance = float('inf')

    for box in boxes:
        box_centroid = ((box[0]['x'] + box[2]['x']) / 2, (box[0]['y'] + box[2]['y']) / 2)
        box_area = (box[2]['x'] - box[0]['x']) * (box[2]['y'] - box[0]['y'])

        distance = math.sqrt((target_centroid[0] - box_centroid[0])**2 + (target_centroid[1] - box_centroid[1])**2)
        area_difference = abs(target_area - box_area)

        total_difference = distance + area_difference

        if total_difference < closest_distance:
            closest_distance = total_difference
            closest_box = box


    def clean_text(text):
    chars_to_remove = [",", ".", "'"]
    for char in chars_to_remove:
        text = text.replace(char, "")
    return text

text = "John's address is 1234 Main St., Anytown, USA."
cleaned_text = clean_text(text)
print(cleaned_text)

    return closest_box

# Get all paragraph bounding boxes
paragraph_boxes = []
for page in result.document.pages:
    for paragraph in page.paragraphs:
        box = [{'x': vertex.x, 'y': vertex.y} for vertex in paragraph.bounding_poly.normalized_vertices]
        paragraph_boxes.append(box)

closest_box = find_closest_box(target_box, paragraph_boxes)

print('The closest box to the target is:', closest_box)



def calculate_iou(box1, box2):
    """
    Calculate the Intersection over Union (IoU) of two bounding boxes.
    
    Parameters:
    box1, box2 -- dictionaries containing the 'x' and 'y' coordinates of the top left 
    and bottom right corners of each bounding box. The coordinates are assumed to be normalized.

    Returns:
    iou -- scalar
    """
    
    # Calculate the (x, y)-coordinates of the intersection rectangle
    xA = max(box1[0]['x'], box2[0]['x'])
    yA = max(box1[0]['y'], box2[0]['y'])
    xB = min(box1[2]['x'], box2[2]['x'])
    yB = min(box1[2]['y'], box2[2]['y'])

    # Compute the area of intersection rectangle
    interArea = max(0, xB - xA) * max(0, yB - yA)

    # Compute the area of both the prediction and ground-truth rectangles
    box1Area = (box1[2]['x'] - box1[0]['x']) * (box1[2]['y'] - box1[0]['y'])
    box2Area = (box2[2]['x'] - box2[0]['x']) * (box2[2]['y'] - box2[0]['y'])

    # Compute the intersection over union by taking the intersection area and dividing it by the sum of 
    # prediction + ground-truth areas - the interesection area
    iou = interArea / float(box1Area + box2Area - interArea)

    # Return the intersection over union
    return iou

def find_best_match_box(target_box, boxes):
    max_iou = 0
    best_match_box = None

    for box in boxes:
        iou = calculate_iou(target_box, box)

        if iou > max_iou:
            max_iou = iou
            best_match_box = box

    if best_match_box is None:  # No overlapping boxes found, find closest box
        best_match_box = find_closest_box(target_box, boxes)

    return best_match_box



from word2number import w2n

def is_number(string):
    try:
        num = w2n.word_to_num(string)
        return True
    except ValueError:
        return False

print(is_number("Two hundred")) # Output: True
print(is_number("Three thousand")) # Output: True
print(is_number("Hello world")) # Output: False

def get_recipient(check_text):
    # Find the position of the start of the target string
    start = check_text.find("Pay to the Order of")
    
    # If the target string is not found, return an indication of failure
    if start == -1:
        return None

    # Calculate the position of the end of the target string
    end = start + len("Pay to the Order of")

    # Extract and return the next string in the text
    # We assume here that the recipient's name is the next string and 
    # is separated by a space or new line. Change this as needed.
    recipient = check_text[end:].split()[0]
    return recipient


from fuzzywuzzy import fuzz

def name_in_sentence(name, sentence):
    # Split the name and the sentence into words
    name_parts = name.split(' ')
    sentence_parts = sentence.split(' ')

    # Initialize the maximum similarity to 0
    max_similarity = 0

    # Compare every part of the name to every part of the sentence
    for part1 in name_parts:
        for part2 in sentence_parts:
            similarity = fuzz.ratio(part1, part2)
            
            # If this is the maximum similarity found so far, update max_similarity
            if similarity > max_similarity:
                max_similarity = similarity

    return max_similarity
similarity = name_in_sentence('John Doe', 'This check is for John Doe.')
print(similarity)  # Output: 100
similarity = name_in_sentence('John Doe', 'The recipient is Johm Doe.')
print(similarity)  # Output: 89
similarity = name_in_sentence('John Doe', 'Doe, John is the recipient.')
print(similarity)  # Output: 100

def clean_text(text):
    chars_to_remove = [",", ".", "'"]
    for char in chars_to_remove:
        text = text.replace(char, "")
    return text

text = "John's address is 1234 Main St., Anytown, USA."
cleaned_text = clean_text(text)
print(cleaned_text)


import re

def remove_single_letter_words(text):
    return re.sub(r'\b\w\b', '', text)

text = "I am John Doe and I live on a 1234 Main St."
cleaned_text = remove_single_letter_words(text)
print(cleaned_text)



import re

def clean_spaces(text):
    # Replace multiple spaces with single space
    text = re.sub(' +', ' ', text)
    # Strip leading and trailing spaces
    text = text.strip()
    return text

text = "  I   am   John   Doe   and   I   live   on   a   1234   Main   St.   "
cleaned_text = clean_spaces(text)
print(cleaned_text)  # Output: "I am John Doe and I live on a 1234 Main St."
