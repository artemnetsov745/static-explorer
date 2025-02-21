import os
import hashlib


def get_file_hash(file_path, hash_algorithm="sha3_256"):
    hash_function = getattr(hashlib, hash_algorithm)()
    with open(file_path, "rb") as file:
        while chunk := file.read(8192):
            hash_function.update(chunk)
    
    return hash_function.hexdigest()


# recursive directory traversal with calculation of hashes of necessary files
def get_dir_hashes(directory_path, extensions=()):
    file_hashes = []
    for entry in os.listdir(directory_path):
        path = os.path.join(directory_path, entry)

        if os.path.isdir(path):
            file_hashes.extend(get_dir_hashes(path, extensions))
        else:
            if extensions and not any(entry.lower().endswith(ext.lower()) for ext in extensions):
                continue

            file_hash = get_file_hash(path)
            file_hashes.append(file_hash)

    return file_hashes


# list comparison
def compare_hashes(site_hashes, repo_hashes):
    return set(site_hashes).issubset(repo_hashes)
