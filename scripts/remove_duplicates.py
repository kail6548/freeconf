import sys
import re

def normalize_config(line):
    # حذف فاصله‌ها، حروف بزرگ کوچک و کاراکترهای اضافی
    return line.strip()

def main(input_file, output_file):
    seen = set()
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    with open(output_file, 'w', encoding='utf-8') as f_out:
        for line in lines:
            if not line.strip():
                continue
            norm = normalize_config(line)
            if norm not in seen:
                seen.add(norm)
                f_out.write(line)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python remove_duplicates.py input.txt output.txt")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
