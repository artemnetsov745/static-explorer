import csv
import json
import re
import subprocess


def RemoveSpecSymbols(content):
    '''
    Removing special characters (now only '\r').

    :param content: Content from which special characters should be removed
    :return: Content without special characters.
    '''

    # Converting the '\r' search template to bytes type
    pattern_bytes = r'\r'.encode('utf-8')

    # Removing the '\r' character
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

    # Combining lists to record each row separately
    data = [commits] + [tags]

    with open('output.csv', 'w', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        for row in data:
            writer.writerow(row)


def SaveToJsonFile(commits, tags):
    '''
    Saving data to a JSON file.

    :param commits: List of commits
    :param tags: List of tags
    '''

    data = {
        "commits": [commits],
        "tags": [tags]
    }

    with open('output.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)