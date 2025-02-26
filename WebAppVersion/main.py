from threading import Thread

from services.static import StaticFilesTraversalService
from .utils.comparison import get_dir_hashes, get_content_hash, compare_hashes
from .utils.filemanager import ClearData, SaveToCsvFile, SaveToJsonFile
from .utils.git_functions import get_commits, get_all_tags, get_target_dir, clone_repository, change_commit, \
    get_all_commits, get_next_commit
from .utils.parser import InitParser


THREADS_AMOUNT = 10

# List of all commits
all_commits_list = []
# List of commits where target dir has been changed
commits_list = []
# List of actual commits
actual_commits = []

# For progress tracking
commits_amount = 0
commits_processed = 0

def process_commits_thread(thread_number, commits_list, target_dir, extensions, site_hashes):
    '''
    Processing commits in a separate thread and adding actual commits to the list of actual commits.

    :param thread_number: Thread number
    :param commits_list: List of commits
    :param target_dir: Target directory in git repository
    :param extensions: Tracked static files extensions
    :param site_hashes: List of hashes of static site files
    '''

    global all_commits_list
    global actual_commits
    global commits_amount
    global commits_processed

    # Get commits for this thread
    if thread_number != THREADS_AMOUNT - 1:
        thread_commits = commits_list[thread_number * int(commits_amount / THREADS_AMOUNT): (thread_number + 1) * int(commits_amount / THREADS_AMOUNT)]
    else:
        thread_commits = commits_list[(THREADS_AMOUNT - 1) * int(commits_amount / THREADS_AMOUNT):]

    # Path to thread local repository
    repo_path = f'.data\\git_files_{thread_number}'

    # Getting a folder with files by commit
    get_target_dir(repo_path, target_dir)

    # Iterating through commits from this thread
    for commit_number in range(len(thread_commits)):
        # Current commit
        commit = thread_commits[commit_number]

        # Change commit (checkout current commit)
        change_commit(commit, repo_path)

        # Getting a list of commit file hashes
        commit_hashes = get_dir_hashes(repo_path + '\\' + target_dir, extensions)

        # Comparing a list of file hashes from a website and a commit
        if compare_hashes(site_hashes, commit_hashes):
            actual_commits.append(commit)
            # Adding commits where target folder hasn't been modified
            next_commit = get_next_commit(all_commits_list, commit)
            while next_commit != '' and next_commit not in commits_list:
                actual_commits.append(next_commit)
                next_commit = get_next_commit(all_commits_list, next_commit)

        # Show progress
        commits_processed += 1
        print(' ' * 100, end='\r')
        print(f'Progress: {commits_processed}/{commits_amount} commits ({round(((commits_processed) / commits_amount) * 100, 2)}%)',end='\r')


def main():
    '''
    Main function.
    '''

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

    print('Cloning repositories...')

    # Cloning git repositories to local folders
    repo_threads = []
    for thread in range(THREADS_AMOUNT):
        thread = Thread(target=clone_repository, args=(args.git, f'.data\\git_files_{thread}',))
        repo_threads.append(thread)
        thread.start()

    # Waiting for all threads completion
    for thread in repo_threads:
        thread.join()

    print('Getting a list of commits...')

    # Getting lists of commits
    global all_commits_list
    all_commits_list = get_all_commits(f'.data\\git_files_0')
    global commits_list
    commits_list = get_commits(f'.data\\git_files_0', args.dir)
    global commits_amount
    commits_amount = len(commits_list)

    print('Processing commits...')

    # List of actual commits
    global actual_commits

    # Iterating through commits in separate threads
    threads = []
    for thread_number in range(THREADS_AMOUNT):
        thread = Thread(target=process_commits_thread, args=(thread_number, commits_list, args.dir,extensions, site_hashes,))
        threads.append(thread)
        thread.start()

    # Waiting for all threads completion
    for thread in threads:
        thread.join()
    print()     # After progress display

    print('Getting actual tags from actual commits...')

    # Getting actual tags from actual commits
    actual_tags = get_all_tags('.data\\git_files_0', actual_commits)
    actual_tags.sort(reverse=True)

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

def EntryPoint():
    try:
        main()
    except Exception as e:
        print(f'An error has occurred: {e}')
    finally:
        # Deleting folders with git repository data
        ClearData('.data')