import sys
import re
from collections import defaultdict

def extract_protocol(line):
    m = re.match(r'^([a-zA-Z0-9\-]+)://', line)
    return m.group(1).lower() if m else "unknown"

def extract_country(line):
    # فرض می‌کنیم کشور در عنوان کانفیگ هست به صورت [IR], [US] و غیره
    m = re.search(r'\[([A-Z]{2})\]', line)
    return m.group(1) if m else "Unknown"

def generate_readme(input_file, output_file):
    protocols = defaultdict(int)
    countries = defaultdict(int)
    total = 0

    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("//"):
                continue
            total += 1
            proto = extract_protocol(line)
            protocols[proto] += 1

            country = extract_country(line)
            countries[country] += 1

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Combined Subscription\n\n")
        f.write(f"**Total configs:** {total}\n\n")

        f.write("## Protocol Distribution\n\n")
        for proto, count in sorted(protocols.items()):
            f.write(f"- {proto}: {count}\n")

        f.write("\n## Country Distribution\n\n")
        for country, count in sorted(countries.items()):
            f.write(f"- {country}: {count}\n")

        f.write("\n---\n")
        f.write("Generated automatically by GitHub Actions\n")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python generate_readme.py input.txt README.md")
        sys.exit(1)
    generate_readme(sys.argv[1], sys.argv[2])
