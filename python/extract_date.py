import re
import os
from datetime import datetime

def extract_date_from_filename(filepath):
    # Extract the filename from the full path
    filename = os.path.basename(filepath)
    
    # Define regex patterns for different date formats with four-digit years
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
                    if pattern == r'(\d{4})-(\d{2})-(\d{2})' or pattern == r'(\d{4})\.(\d{2})\.(\d{2})':
                        year, month, day = int(groups[0]), int(groups[1]), int(groups[2])
                    else:
                         month, day, year = int(groups[0]), int(groups[1]), int(groups[2])
                    date = datetime(year, month, day)
                    return date.strftime('%Y-%m-%d')
            except ValueError:
                # Skip invalid date combinations
                continue

    return None

# Test cases
filepaths = [
    'c:\\path\\to\\filename 12.7.2023.xlsx',
    '/path/to/filename 4.1.2023.txt',
    '/another/path/filename_4.1.2023.txt',
    '/different/path/filename 2023-04-01.txt',
    '/another/one/someotherfilename 4.1.2023.txt',
    '/last/one/otherfilename 2023-04-01.txt',
    'c:\\path\\to\\filename 01.01.2023.xlsx',
    '/path/to/filename 12.31.2023.txt',
    '/another/path/filename_12.31.2023.txt',
    '/different/path/filename 2023-12-31.txt',
    '/another/one/someotherfilename 1.9.2023.txt',
    '/last/one/otherfilename 2023-12-31.txt',
    '/path/to/filename 12/31/2023.txt',
    'c:\\path\\to\\filename 2023.12.31.xlsx',
    'c:\\path\\to\\filename 2023.01.01.xlsx',
    '/path/to/filename 2023-01-01.txt',
    '/another/path/filename_01-01-2023.txt',
    '/another/path/filename_1-9-2023.txt'
]

for filepath in filepaths:
    extracted_date = extract_date_from_filename(filepath)
    print(f"Filepath: {filepath}, Extracted Date: {extracted_date}")
