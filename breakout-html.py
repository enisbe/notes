import pypandoc
from bs4 import BeautifulSoup
import os

# Convert .docx to .html
output = pypandoc.convert_file('your_file.docx', 'html')

soup = BeautifulSoup(output, 'html.parser')

sections = soup.find_all('h1')

# Save content before the first <h1> as cover.html
if sections:
    cover_content = str(soup)[:sections[0].previous_sibling]
    with open("cover.html", "w", encoding="utf-8") as f:
        f.write(cover_content)

# Extract content for each section starting from <h1>
for index, section in enumerate(sections):
    # If this isn't the last section, end the current section at the next <h1>
    if index + 1 < len(sections):
        end = sections[index + 1].position.previous
    else:
        end = None
    
    # Extract section content
    content = str(soup)[sections[index].position:end]

    # Save the section to a new .html file named after the section's content
    filename = section.get_text().strip().replace(" ", "_") + ".html"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)

print("Sections saved successfully!")
