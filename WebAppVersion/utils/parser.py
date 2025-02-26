import argparse


def InitParser():
    parser = argparse.ArgumentParser(description='A console program for determining the versions of web applications based on their static resources')
    # Required argument - the URL of the target site
    parser.add_argument("url", help="The URL of the target site")

    # Required argument - link to the git repository
    parser.add_argument("git", help="Link to the git repository")

    # Required argument - the path to the folder in the git repository
    parser.add_argument("dir", help="The path to the folder in the git repository")

    # Optional argument - extensions of the target files
    parser.add_argument("-e", "--extensions", nargs='*', help="Extensions of the target files")

    # Optional argument - saving the result to a CSV file
    parser.add_argument("-c", "--csv", action='store_true', help="Saving the result to a CSV file")

    # Optional argument - saving the result to a JSON file
    parser.add_argument("-j", "--json", action='store_true', help="Saving the result to a JSON file")

    return parser