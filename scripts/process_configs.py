import sys
import re
import os
from collections import defaultdict

def normalize_config(line):
    return line.strip()

def extract_protocol(line):
    m = re.match(r'^([a-zA-Z0-9\-]+)://', line)
    return m.group(1).lower() if m else "unknown"

def extract_country(line):
    # فرض: کشور داخل براکت بزرگ [US], [IR] و ...
    m = re.search(r'\[([A-Z]{2})\]', line)
    return m.group(1) if m else "unknown"

def extract_security(line):
    # فرض: "tls" یا "notls" در کانفیگ وجود دارد یا خیر
    if "tls" in line.lower():
        return "tls"
    else:
        return "notls"

def main(input_file, output_dir, repo_url):
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(os.path.join(output_dir, "protocol"), exist_ok=True)
    os.makedirs(os.path.join(output_dir, "country"), exist_ok=True)
    os.makedirs(os.path.join(output_dir, "security"), exist_ok=True)

    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    seen = set()
    configs = []

    for line in lines:
        norm = normalize_config(line)
        if norm and norm not in seen and re.match(r'^[a-zA-Z0-9\-]+://', norm):
            seen.add(norm)
            configs.append(norm)

    # دسته‌بندی
    by_protocol = defaultdict(list)
    by_country = defaultdict(list)
    by_security = defaultdict(list)

    for c in configs:
        p = extract_protocol(c)
        co = extract_country(c)
        se = extract_security(c)
        by_protocol[p].append(c)
        by_country[co].append(c)
        by_security[se].append(c)

    # تابع ذخیره فایل‌ها با base64
    import base64

    def save_base64_file(path, lines):
        data = "\n".join(lines).encode('utf-8')
        b64data = base64.b64encode(data).decode('utf-8')
        with open(path, 'w', encoding='utf-8') as f:
            f.write(b64data)

    # ذخیره همه در یک فایل
    save_base64_file(os.path.join(output_dir, "combined_base64.txt"), configs)

    # ذخیره بر اساس پروتکل
    for k, v in by_protocol.items():
        save_base64_file(os.path.join(output_dir, "protocol", f"{k}.txt"), v)

    # ذخیره بر اساس کشور
    for k, v in by_country.items():
        save_base64_file(os.path.join(output_dir, "country", f"{k}.txt"), v)

    # ذخیره بر اساس امنیت
    for k, v in by_security.items():
        save_base64_file(os.path.join(output_dir, "security", f"{k}.txt"), v)

    # ساخت README با لینک فایل‌ها
    # فرض می‌کنیم repo_url مثل "https://github.com/username/repo" است و branch main است
    raw_base = repo_url.rstrip('/') + "/raw/main/" + output_dir + "/"

    def file_link(path):
        return f"{raw_base}{path}"

    total = len(configs)

    with open("README.md", 'w', encoding='utf-8') as f:
        f.write("# Combined Subscription\n\n")
        f.write(f"**Total configs:** {total}\n\n")

        f.write("## Protocol Links\n\n")
        for k in sorted(by_protocol.keys()):
            link = file_link(f"protocol/{k}.txt")
            f.write(f"- [{k}]({link}) ({len(by_protocol[k])} configs)\n")

        f.write("\n## Country Links\n\n")
        for k in sorted(by_country.keys()):
            link = file_link(f"country/{k}.txt")
            f.write(f"- [{k}]({link}) ({len(by_country[k])} configs)\n")

        f.write("\n## Security Links\n\n")
        for k in sorted(by_security.keys()):
            link = file_link(f"security/{k}.txt")
            f.write(f"- [{k}]({link}) ({len(by_security[k])} configs)\n")

        f.write("\n---\nGenerated automatically by GitHub Actions\n")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python process_configs.py input.txt output_dir repo_url")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2], sys.argv[3])
