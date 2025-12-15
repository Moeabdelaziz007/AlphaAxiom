#!/usr/bin/env python3
"""
AST-safe emoji cleaner - uses Python tokenizer to only modify comments,
leaving string literals untouched.
"""
import tokenize
import io
import re
import sys
import os

# Emoji pattern for removal
EMOJI_PATTERN = re.compile(
    "["
    "\U0001F300-\U0001F9FF"  # Emoji Symbols
    "\U00002600-\U000027BF"  # Misc symbols, Dingbats  
    "\U0001FA00-\U0001FAFF"  # Symbols Extended-A
    "\U00002300-\U000023FF"  # Misc Technical
    "\U0000FE00-\U0000FE0F"  # Variation Selectors
    "\U0001F000-\U0001F02F"  # Mahjong, Domino
    "]+",
    flags=re.UNICODE
)

# Character replacements
CHAR_REPLACEMENTS = {
    '\u00d7': '*',    # × multiplication
    '\u03c3': 'sigma', # σ
    '\u2248': '~',    # ≈
    '\u2192': '->',   # →
    '\u2190': '<-',   # ←
    '\u2501': '-',    # ━ box drawing
    '\u2500': '-',    # ─ box drawing
    '\u2502': '|',    # │ box drawing
    '\u2019': "'",    # ' curly apostrophe
    '\u2018': "'",    # ' curly apostrophe  
    '\u201c': '"',    # " curly quote
    '\u201d': '"',    # " curly quote
}

def clean_string(s):
    """Remove emojis and replace special chars."""
    # Remove emojis
    s = EMOJI_PATTERN.sub('', s)
    # Replace special characters
    for char, replacement in CHAR_REPLACEMENTS.items():
        s = s.replace(char, replacement)
    return s

def clean_file_safe(filepath):
    """Clean only comments, leave string content as-is."""
    with open(filepath, 'rb') as f:
        source = f.read()
    
    try:
        tokens = list(tokenize.tokenize(io.BytesIO(source).readline))
    except tokenize.TokenizeError as e:
        print(f"Tokenize error in {filepath}: {e}")
        # Fall back to simple cleaning
        return clean_file_simple(filepath)
    
    modified = False
    result_tokens = []
    
    for tok in tokens:
        if tok.type == tokenize.COMMENT:
            # Clean comments
            new_string = clean_string(tok.string)
            if new_string != tok.string:
                modified = True
            result_tokens.append(tok._replace(string=new_string))
        elif tok.type == tokenize.STRING:
            # For strings, only replace critical chars (curly quotes)
            new_string = tok.string
            for char in ['\u2019', '\u2018', '\u201c', '\u201d']:
                if char in new_string:
                    new_string = new_string.replace(char, CHAR_REPLACEMENTS[char])
                    modified = True
            # Remove emojis from strings too (they break Cloudflare)
            new_clean = EMOJI_PATTERN.sub('', new_string)
            if new_clean != new_string:
                modified = True
                new_string = new_clean
            result_tokens.append(tok._replace(string=new_string))
        else:
            result_tokens.append(tok)
    
    if modified:
        # Reconstruct source
        result = tokenize.untokenize(result_tokens)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(result.decode('utf-8') if isinstance(result, bytes) else result)
        return True
    return False

def clean_file_simple(filepath):
    """Simple fallback cleaning for files that can't tokenize."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    content = clean_string(content)
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python clean_emojis_safe.py <directory>")
        sys.exit(1)
    
    directory = sys.argv[1]
    modified = 0
    errors = 0
    
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                try:
                    if clean_file_safe(filepath):
                        print(f"Cleaned: {filepath}")
                        modified += 1
                except Exception as e:
                    print(f"Error with {filepath}: {e}")
                    errors += 1
    
    print(f"\nTotal files modified: {modified}, Errors: {errors}")

if __name__ == "__main__":
    main()
