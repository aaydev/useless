# get_fobobj_filter.py
# Extracts object IDs from exported .fob file of MS Dynamics NAV / Business Central
# Truncates data at \x1a\x1a, parses objects, groups by type with range merging
# Author: Alexey Anisimov, linkedin.com/in/aaydev

import re
import sys
from collections import defaultdict

def analyze_nav_file(input_file_path, output_file_path='filter_results.txt'):
    objects = defaultdict(list)

    # Patterns to extract object IDs
    patterns = [
        (r'Record\s+(\d+)', 'Table'),
        (r'Codeunit\s+(\d+)', 'Codeunit'),
        (r'Page\s+(\d+)', 'Page'),
        (r'Report\s+(\d+)', 'Report'),
        (r'Table\s+(\d+)', 'Table'),
        (r'XMLport\s+(\d+)', 'XMLport'),
        (r'MenuSuite\s+(\d+)', 'MenuSuite'),
        (r'Query\s+(\d+)', 'Query'),
        (r'Form\s+(\d+)', 'Form'),
        (r'Dataport\s+(\d+)', 'Dataport'),
    ]

    try:
        # Read file in binary mode to correctly handle 0x1A
        with open(input_file_path, 'rb') as f:
            content_bytes = f.read()

        # Find position of \x1a\x1a (0x1A 0x1A) — end of object catalog
        stop_marker = b'\x1a\x1a'
        stop_pos = content_bytes.find(stop_marker)

        if stop_pos != -1:
            content_bytes = content_bytes[:stop_pos]
            print(f"📌 Stopped at position: {stop_pos} (\\x1a\\x1a marker found)")
        else:
            print("⚠️  \\x1a\\x1a marker not found. Using entire file.")

        # Decode using cp866 (OEM-866)
        try:
            content = content_bytes.decode('cp866')
        except UnicodeDecodeError as e:
            print(f"❌ Decoding error (cp866): {e}")
            sys.exit(1)

        # Find all matches
        for pattern, obj_type in patterns:
            matches = re.findall(pattern, content)
            for obj_id in matches:
                objects[obj_type].append(int(obj_id))

        # Remove duplicates and sort
        for obj_type in objects:
            objects[obj_type] = sorted(set(objects[obj_type]))

        # Group into ranges
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
            # Last range
            if start == end:
                ranges.append(str(start))
            else:
                ranges.append(f"{start}..{end}")

            result_lines.append(f"{obj_type}:")
            result_lines.append("|".join(ranges))

        # Save result
        with open(output_file_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(result_lines))

        print(f"✅ Processing completed. Results saved to '{output_file_path}'")
        print("\n" + "\n".join(result_lines))

    except FileNotFoundError:
        print(f"❌ Error: File '{input_file_path}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unknown error: {e}")
        sys.exit(1)

# === Entry point ===
if __name__ == "__main__":
    print("🚀 Script: get_fobobj_filter.py")
    print("👤 (c) 2025, Alexey Anisimov, linkedin.com/in/aaydev")
    print("-" * 50)

    if len(sys.argv) != 2:
        print("📌 Usage: python get_fobobj_filter.py <file.fob>")
        sys.exit(1)

    input_path = sys.argv[1]
    analyze_nav_file(input_path)