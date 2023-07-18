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



from PIL import Image, ImageDraw

# Load your image
image = Image.open('your_image_file.png')

# Assume your bounding_poly normalized vertices
normalized_vertices = [
    {'x': 0.1, 'y': 0.1},
    {'x': 0.1, 'y': 0.2},
    {'x': 0.2, 'y': 0.2},
    {'x': 0.2, 'y': 0.1}
]

# Convert normalized vertices to pixel space
vertices = [{'x': v['x'] * image.width, 'y': v['y'] * image.height} for v in normalized_vertices]

# Draw bounding box
draw = ImageDraw.Draw(image)
draw.polygon([
    vertices[0]['x'], vertices[0]['y'],
    vertices[1]['x'], vertices[1]['y'],
    vertices[2]['x'], vertices[2]['y'],
    vertices[3]['x'], vertices[3]['y']
], outline='red')

# Save the image
image.save('image_with_bounding_box.png')
