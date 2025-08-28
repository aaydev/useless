# fix_poedit_bcxlf.py
# Fix some tags for BC365 xlf files produced by POEdit
# Author: Alexey Anisimov, linkedin.com/in/aaydev

import re
import os
import sys

def fix_empty_tags(input_file):
    # Check if the file exists
    if not os.path.isfile(input_file):
        print(f"File not found: {input_file}")
        return

    # Read file content
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Regular expression for tags: <tag ...></tag>
    # Works for 'note' and 'target' and 'source' (case-sensitive!)
    # Removes whitespace between opening and closing tags and converts them to self-closing
    pattern = r'<(note|target|source)([^>]*)>\s*</\1>'

    # Replacement: <note .../> or <target .../> or <source .../>
    replacement = r'<\1\2/>'

    # Perform replacement
    fixed_content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)

    # Generate output file name
    base, ext = os.path.splitext(input_file)
    output_file = f"{base}-fixed{ext}"

    # Write the result to a new file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(fixed_content)

    print(f"File processed successfully. Result saved to: {output_file}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python fix_poedit_bcxlf.py <path_to_file.xlf>")
    else:
        fix_empty_tags(sys.argv[1])