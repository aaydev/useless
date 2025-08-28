# get_txtobj_filter.py
# Extracts object IDs from exported .txt file of MS Dynamics NAV / Business Central
# Truncates data at \x1a\x1a, parses objects, groups by type with range merging
# Author: Alexey Anisimov, linkedin.com/in/aaydev

import re
import sys
from collections import defaultdict

def analyze_nav_export(input_file_path, output_file_path='filter_results.txt'):
    # Dictionary to store IDs by object type
    objects = defaultdict(list)

    # Regular expression to find lines: OBJECT Type ID ...
    pattern = re.compile(r'^OBJECT\s+([A-Za-z]+)\s+(\d+)', re.MULTILINE)

    try:
        # Read file using OEM-866 encoding (cp866)
        with open(input_file_path, 'r', encoding='cp866') as file:
            content = file.read()

        # Find all matches
        matches = pattern.findall(content)
        for obj_type, obj_id in matches:
            objects[obj_type].append(int(obj_id))

        # Remove duplicates and sort
        for obj_type in objects:
            objects[obj_type] = sorted(set(objects[obj_type]))

        # Group into ranges (e.g. 50049|50050..50055)
        result_lines = []
        for obj_type in sorted(objects.keys()):
            ids = objects[obj_type]
            if not ids:
                continue

            ranges = []
            start = end = ids[0]

            for i in range(1, len(ids)):
                if ids[i] == end + 1:
                    end = ids[i]
                else:
                    if start == end:
                        ranges.append(str(start))
                    else:
                        ranges.append(f"{start}..{end}")
                    start = end = ids[i]
            # Add the last range
            if start == end:
                ranges.append(str(start))
            else:
                ranges.append(f"{start}..{end}")

            result_lines.append(f"{obj_type}:")
            result_lines.append("|".join(ranges))

        # Save result in UTF-8 (for proper readability)
        with open(output_file_path, 'w', encoding='utf-8') as out_file:
            out_file.write("\n".join(result_lines))

        print(f"✅ File processed successfully. Results saved to '{output_file_path}'")
        print("\n" + "\n".join(result_lines))

    except FileNotFoundError:
        print(f"❌ Error: File '{input_file_path}' not found.")
        sys.exit(1)
    except UnicodeDecodeError as e:
        print(f"❌ Decoding error (cp866): {e}")
        print("Make sure the file is encoded in OEM-866.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

# === Entry point ===
if __name__ == "__main__":
    print("🚀 Script: get_txtobj_filter.py")
    print("👤 (c) 2025, Alexey Anisimov, linkedin.com/in/aaydev")
    print("-" * 50)

    if len(sys.argv) != 2:
        print("📌 Usage: python get_txtobj_filter.py <file.txt>")
        sys.exit(1)

    input_path = sys.argv[1]
    analyze_nav_export(input_path)