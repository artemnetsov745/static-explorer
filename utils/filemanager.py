import re
import subprocess


def RemoveSpecSymbols(content):
    # Преобразование шаблона для поиска '\r' к типу bytes
    pattern_bytes = r'\r'.encode('utf-8')
    # Удаление символа '\r'
    cleaned_content = re.sub(pattern_bytes, b'', content)
    return cleaned_content


def ClearData(dir_path):
    '''
    Recursively deleting a folder.

    :param dir_path: Folder path
    '''

    try:
        subprocess.run(['.\\utils\\remove_folder.bat', dir_path], shell=False)
    except subprocess.CalledProcessError as e:
        print(f"An error has occurred: {e}")


def SaveToCsvFile(commits, tags):
    '''
    Saving data to a CSV file.

    :param commits: List of commits
    :param tags: List of tags
    '''

    print('SaveToCsvFile')

def SaveToJsonFile(commits, tags):
    '''
    Saving data to a JSON file.

    :param commits: List of commits
    :param tags: List of tags
    '''

    print('SaveToJsonFile')