#!/usr/bin/env python3
"""Safe emoji remover that preserves Python syntax."""
import re
import sys
import os

# Unicode ranges for emojis and problematic characters
EMOJI_PATTERN = re.compile(
    "["
    "\U0001F300-\U0001F9FF"  # Emoji Symbols
    "\U00002600-\U000027BF"  # Misc symbols, Dingbats
    "\U0001FA00-\U0001FAFF"  # Symbols and Pictographs Extended-A
    "\U00002B50-\U00002B55"  # Stars, misc
    "\U0000FE00-\U0000FE0F"  # Variation Selectors
    "\U0001F000-\U0001F02F"  # Mahjong, Domino
    "\U00002300-\U000023FF"  # Misc Technical
    "]+",
    flags=re.UNICODE
)

# Characters to replace (with ASCII equivalents)
REPLACEMENTS = {
    '×': '*',     # Multiplication sign
    '÷': '/',     # Division sign
    'σ': 'sigma', # Greek sigma
    '≈': '~',     # Approx equal
    '→': '->',    # Arrow
    '←': '<-',    # Left arrow
    '━': '-',     # Box drawing
    '─': '-',     # Box drawing
    '│': '|',     # Box drawing
    '⭐': '*',    # Star
    '✓': 'OK',    # Checkmark
    '✗': 'X',     # X mark
}

def clean_file(filepath):
    """Remove emojis while preserving syntax."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # Step 1: Remove emoji patterns
    content = EMOJI_PATTERN.sub('', content)
    
    # Step 2: Replace specific characters
    for char, replacement in REPLACEMENTS.items():
        content = content.replace(char, replacement)
    
    # Step 3: Remove any standalone Arabic/non-Latin text in comments only
    # This regex finds comments with Arabic characters and removes the Arabic parts
    def clean_arabic_in_comment(match):
        line = match.group(0)
        # Keep English + code, remove Arabic characters
        cleaned = re.sub(r'[\u0600-\u06FF\u0750-\u077F]+', '', line)
        return cleaned
    
    # Apply to lines starting with # (comments)
    content = re.sub(r'#.*$', clean_arabic_in_comment, content, flags=re.MULTILINE)
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python clean_emojis.py <directory>")
        sys.exit(1)
    
    directory = sys.argv[1]
    modified = 0
    
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                try:
                    if clean_file(filepath):
                        print(f"Cleaned: {filepath}")
                        modified += 1
                except Exception as e:
                    print(f"Error with {filepath}: {e}")
    
    print(f"\nTotal files modified: {modified}")

if __name__ == "__main__":
    main()
