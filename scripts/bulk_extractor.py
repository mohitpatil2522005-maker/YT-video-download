import sqlite3
import re
import pyperclip
import pytesseract
from PIL import Image
import os
import sys

# Configure pytesseract to point to the typical Windows install path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

DB_PATH = 'memory.db'

def init_db():
    """Initialize SQLite database for checking duplicate URLs."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS videos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            url TEXT UNIQUE
        )
    ''')
    conn.commit()
    return conn

def extract_data_from_image(image_path):
    """Use PyTesseract to extract text from a high-res image."""
    try:
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img)
        print("--- OCR Extracted Text ---")
        print(text)
        print("--------------------------\n")
        return text
    except Exception as e:
        print(f"Error reading image: {e}")
        return ""

def parse_text(text):
    """Parse video titles followed by URLs using Regex."""
    url_pattern = re.compile(r'(https?://[^\s]+)')
    lines = text.split('\n')
    results = []
    
    current_title = ""
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        match = url_pattern.search(line)
        if match:
            url = match.group(0)
            # Find the title which is the preceding lines
            # If the url is on the same line, remove the url slightly
            line_without_url = line.replace(url, '').strip()
            if line_without_url:
                current_title += " " + line_without_url
                
            title = current_title.strip() if current_title.strip() else "Unknown Title"
            results.append((title, url))
            current_title = "" # Reset for next
        else:
            # Append lines assuming they are titles
            current_title += " " + line
            
    return results

def process_and_store(conn, data):
    """Store data to SQLite, copy to clipboard, and return counts."""
    cursor = conn.cursor()
    new_entries = 0
    duplicates = 0
    
    for title, url in data:
        try:
            cursor.execute('INSERT INTO videos (title, url) VALUES (?, ?)', (title, url))
            new_entries += 1
        except sqlite3.IntegrityError:
            duplicates += 1
            
    conn.commit()
    
    # Copy parsed entries to clipboard and save them to text file
    if data:
        urls_only = [u for t, u in data]
        
        # Ensure New folder exists
        os.makedirs('New folder', exist_ok=True)
        output_path = os.path.join('New folder', 'yt copy links.txt')
        
        # Write only URLs to the file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(urls_only) + '\n')
            
        clipboard_text = "\n".join(urls_only)
        pyperclip.copy(clipboard_text)
        print("Copied all URLs to clipboard and saved to 'yt copy links.txt'.\n")
        
    return new_entries, duplicates

def generate_report(new_entries, duplicates):
    """Generates a summary report of the processed data."""
    print("=== Summary Report ===")
    print(f"New URLs added: {new_entries}")
    print(f"Duplicate URLs skipped: {duplicates}")
    print("======================\n")

def main(image_path):
    print(f"Processing image: {image_path}\n")
    if not os.path.exists(image_path):
        print("Error: Image not found.")
        return

    conn = init_db()
    
    text = extract_data_from_image(image_path)
    if not text.strip():
        print("No text found in image.")
        return
        
    data = parse_text(text)
    if not data:
        print("No URLs parsed from the image.")
        return
        
    new_entries, duplicates = process_and_store(conn, data)
    generate_report(new_entries, duplicates)
    
if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        print("Usage: python bulk_extractor.py <path_to_image>")
