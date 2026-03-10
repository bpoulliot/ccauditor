import hashlib


def compute_hash(text):

    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def detect_duplicate_content(contents):

    seen = {}

    duplicates = []

    for item in contents:

        h = compute_hash(item["text"])

        if h in seen:

            duplicates.append(
                {
                    "original": seen[h],
                    "duplicate": item,
                }
            )

        else:

            seen[h] = item

    return duplicates
