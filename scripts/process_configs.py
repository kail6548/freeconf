import sys
import re
import os
from collections import defaultdict
import base64
from urllib.parse import urlparse

def normalize_config(line):
    return line.strip()

def extract_protocol(line):
    m = re.match(r'^([a-zA-Z0-9\-]+)://', line)
    return m.group(1).lower() if m else "unknown"

def extract_country(line):
    m = re.search(r'\[([A-Z]{2})\]', line)
    return m.group(1) if m else "unknown"

def extract_security(line):
    # نمونه ساده، بهبود دلخواه
    if "tls" in line.lower():
        return "tls"
    else:
        return "notls"

def save_base64_file(path, lines):
    data = "\n".join(lines).encode('utf-8')
    b64data = base64.b64encode(data).decode('utf-8')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(b64data)

def parse_github_url(repo_url):
    # مثال: https://github.com/username/reponame
    parts = urlparse(repo_url)
    path_parts = parts.path.strip('/').split('/')
    if len(path_parts) >= 2:
        return path_parts[0], path_parts[1]
    else:
        return None, None

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

    save_base64_file(os.path.join(output_dir, "combined_base64.txt"), configs)

    for k, v in by_protocol.items():
        save_base64_file(os.path.join(output_dir, "protocol", f"{k}.txt"), v)

    for k, v in by_country.items():
        save_base64_file(os.path.join(output_dir, "country", f"{k}.txt"), v)

    for k, v in by_security.items():
        save_base64_file(os.path.join(output_dir, "security", f"{k}.txt"), v)

    repo_owner, repo_name = parse_github_url(repo_url)
    if not repo_owner or not repo_name:
        print("❌ Invalid GitHub repo URL")
        return

    raw_base = f"https://raw.githubusercontent.com/{repo_owner}/{repo_name}/main/{output_dir}/"

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
