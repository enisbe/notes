import re
from datetime import datetime

def extract_date_from_filename(filename):
    # Define regex patterns for different date formats
    date_patterns = [
        r'(\d{1,2})\.(\d{1,2})\.(\d{4})', # Matches '4.1.2023' or '04.01.2023'
        r'(\d{4})-(\d{2})-(\d{2})',       # Matches '2023-04-01'
        r'(\d{1,2})-(\d{1,2})-(\d{4})',   # Matches '4-1-2023' or '04-01-2023'
        r'(\d{4})\.(\d{2})\.(\d{2})',     # Matches '2023.04.01'
        r'(\d{1,2})/(\d{1,2})/(\d{4})'    # Matches '4/1/2023' or '04/01/2023'
    ]

    for pattern in date_patterns:
        match = re.search(pattern, filename)
        if match:
            groups = match.groups()
            try:
                # Attempt to construct a date object
                if len(groups) == 3:
                    day, month, year = int(groups[0]), int(groups[1]), int(groups[2])
                    date = datetime(year, month, day)
                    return date.strftime('%Y-%m-%d')
            except ValueError:
                # Skip invalid date combinations
                continue

    return None

# Test cases
filenames = [
    'filename 4.1.2023.txt',
    'filename_4.1.2023.txt',
    'filename 2023-04-01.txt',
    'someotherfilename 4.1.2023.txt',
    'otherfilename 2023-04-01.txt'
]

for fname in filenames:
    extracted_date = extract_date_from_filename(fname)
    print(f"Filename: {fname}, Extracted Date: {extracted_date}")
