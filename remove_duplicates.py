seen = set()
with open("combined.txt", "r") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        if line.startswith("//"):
            print(line)
            continue
        if "://" not in line:
            continue
        key = line.split('#')[0].lower()
        if key not in seen:
            seen.add(key)
            print(line)
