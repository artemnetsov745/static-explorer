import subprocess

repo_url = "https://github.com/jquery/jquery.git" #для примера
#директория для хранения локального репозитория
repo_dir = "jquery" #для примера
#целевая папка из задания
target_dir = "test/data"#для примера

def get_commits(repo_url, repo_dir, target_dir):
    """Функция частичного клонирования репозитория и получения списка коммитов для целевой директории"""
    try:
        # Клонирование репозитория
        subprocess.run(
            ["git", "clone", "--filter=blob:none", "--no-checkout", repo_url, repo_dir],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        # Получение списка коммитов для целевой директории
        commits_output = subprocess.run(
            ["git", "-C", repo_dir, "log", "--oneline", "--", target_dir],
            capture_output=True, text=True, check=True, stderr=subprocess.DEVNULL
        )
        commits = [line.split()[0] for line in commits_output.stdout.strip().split("\n")]
        return commits

    except subprocess.CalledProcessError as error:
        print(f"Ошибка при клонировании или получении коммитов: {error}")
        return []

def get_target_dir(commit, repo_dir, target_dir):
    """Функция загрузки целевой директории"""
    try:
        """Инициализация sparse-checkout в склонированном репозитории"""
        subprocess.run(
            ["git", "-C", repo_dir, "sparse-checkout", "init"],
            check=True, stderr=subprocess.DEVNULL
        )
        """Установка директории для частичной загрузки sparse-checkout"""
        subprocess.run(
            ["git", "-C", repo_dir, "sparse-checkout", "set", "--no-cone", target_dir],
            check=True, stderr=subprocess.DEVNULL
        )
        """Загрузка целевой директории по хэшу коммита"""
        subprocess.run(
            ["git", "-C", repo_dir, "checkout", commit],
            check=True, stderr=subprocess.DEVNULL
        )
    except subprocess.CalledProcessError as error:
        print(f"Ошибка при выполнении команды sparse-checkout или checkout: {error}")

def get_commit_tags(repo_dir, commit):
    """Функция получения тегов для определенного коммита"""
    try:
        result = subprocess.run(
            ["git", "-C", repo_dir, "tag", "--points-at", commit],
            capture_output=True, text=True, check=True, stderr=subprocess.DEVNULL
        )
        tag_list = result.stdout.strip().split("\n")
        return [tag for tag in tag_list if tag]
    except subprocess.CalledProcessError as error:
        print(f"Ошибка при получении тегов для коммита {commit}: {error}")
        return []

def get_all_tags(repo_dir, commit_list):
    """Функция получения списка тегов для списка коммитов"""
    all_tags = []
    for commit in commit_list:
        current_tags = get_commit_tags(repo_dir, commit)
        all_tags.extend(current_tags)
    return all_tags
