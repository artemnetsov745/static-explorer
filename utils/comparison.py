import os
import hashlib

from utils.filemanager import RemoveSpecSymbols


def get_content_hash(file_content, hash_algorithm="sha3_256"):
    '''
    The function of calculating the hash of a file by its contents.

    :param file_content: File content
    :param hash_algorithm: Hash algorithm, by default is sha3_256
    :return: Hash of the file contents as a hex string.
    '''

    hash_function = getattr(hashlib, hash_algorithm)()
    cleaned_file_content = RemoveSpecSymbols(file_content)
    hash_function.update(cleaned_file_content)
    return hash_function.hexdigest()


def get_file_hash(file_path, hash_algorithm="sha3_256"):
    hash_function = getattr(hashlib, hash_algorithm)()
    with open(file_path, "rb") as file:
        while chunk := file.read(8192):
            hash_function.update(RemoveSpecSymbols(chunk))

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