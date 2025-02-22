from services.static import StaticFilesTraversalService
from utils.comparison import get_dir_hashes, get_content_hash, compare_hashes
from utils.filemanager import ClearData, SaveToCsvFile, SaveToJsonFile, RemoveSpecSymbols
from utils.git_functions import get_commits, get_all_tags, get_target_dir
from utils.parser import InitParser


def main():
    # Parser for arguments when running from the console
    parser = InitParser()

    # Parsing arguments
    args = parser.parse_args()

    # List of static files extensions
    if args.extensions:
        extensions = args.extensions
    else:
        extensions = []

    print('Getting static files from the website...')

    # Getting static files from the website
    static_files = StaticFilesTraversalService(
        base_url=args.url,
    )

    # List of file hashes from the site
    site_hashes = []

    print('Calculating hashes of files from a website...')

    # Calculating hashes of files from a website
    for file in static_files.traverse(max_depth=10):
        file_extention = '.' + file.path.split('.')[-1]  # File extension
        if file_extention in extensions:
            site_hashes.append(get_content_hash(file.content))
            print(f'Processed file: {file.path}')

    print('Getting a list of commits...')

    # Getting a list of commits
    commits_list = get_commits(args.git, f'.data\\git_files', args.dir)
    commits_amount = len(commits_list)

    print('Commits processing...')

    # List of actual commits
    actual_commits = []

    # Iterating through commits
    for commit_number in range(commits_amount):
        # Current commit
        commit = commits_list[commit_number]

        # Getting a folder with files by commit
        get_target_dir(commit, '.data\\git_files', args.dir)

        # Getting a list of commit file hashes
        commit_hashes = get_dir_hashes('.data\\git_files\\' + args.dir, extensions)

        # Comparing a list of file hashes from a website and a commit
        if compare_hashes(site_hashes, commit_hashes):
            actual_commits.append(commit)

        # Show progress
        print(' ' * 100, end='\r')
        print(f'Progress: {commit_number + 1}/{commits_amount} commits ({round(((commit_number + 1) / commits_amount) * 100, 2)}%)', end='\r')
    print()

    # Getting tags for actual commits
    actual_tags = get_all_tags('.data\\git_files', actual_commits)

    # Return results
    print()
    print('Actual commits:')
    for commit in actual_commits:
        print(commit)
    print()

    print('Actual tags:')
    for tag in actual_tags:
        print(tag)
    print()

    # Saving results to CVS and JSON
    if args.csv:
        SaveToCsvFile(actual_commits, actual_tags)
    if args.json:
        SaveToJsonFile(actual_commits, actual_tags)

    print('The program is completed!')

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f'An error has occurred: {e}')
    finally:
        # Deleting folders with git repository data
        ClearData('.data')