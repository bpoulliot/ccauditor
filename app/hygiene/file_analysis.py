import hashlib


def compute_file_hash(data):

    return hashlib.sha256(data).hexdigest()


def detect_duplicate_files(files):

    hashes = {}

    duplicates = []

    for file in files:

        h = compute_file_hash(file["data"])

        if h in hashes:

            duplicates.append(
                {
                    "original": hashes[h],
                    "duplicate": file,
                }
            )

        else:

            hashes[h] = file

    return duplicates


def detect_unused_files(files, references):

    unused = []

    referenced = set(references)

    for f in files:

        if f["id"] not in referenced:
            unused.append(f)

    return unused
