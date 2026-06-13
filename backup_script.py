import os
import shutil
from pathlib import Path

HOME = Path.home()

BACKUP_ROOT = HOME / "Desktop" / "backup"

CATEGORIES = {
    "Images": {
        ".jpg", ".jpeg", ".png", ".gif",
        ".bmp", ".webp", ".svg", ".ico",
        ".tiff", ".tif", ".heic", ".raw"
    },

    "PDFs": {
        ".pdf"
    },

    "Text_Files": {
        ".txt", ".md", ".rst"
    },

    "Documents": {
        ".doc", ".docx",
        ".ppt", ".pptx",
        ".xls", ".xlsx",
        ".csv", ".rtf",
        ".odt", ".ods", ".odp"
    },

    "Archives": {
        ".zip", ".rar", ".7z",
        ".tar", ".gz"
    },

    "Videos": {
        ".mp4", ".mkv",
        ".avi", ".mov", ".wmv",
        ".flv", ".webm"
    },

    "Audio": {
        ".mp3", ".wav", ".flac",
        ".aac", ".ogg", ".m4a"
    },

    "Fonts": {
        ".ttf", ".otf", ".woff", ".woff2"
    },

    "Database": {
        ".db", ".sqlite", ".sqlite3"
    }
}

# Extensions to skip completely (make sure your code stays on GitHub)
SKIP_EXTENSIONS = {
    ".py", ".java", ".cpp", ".c", ".h",
    ".js", ".ts", ".jsx", ".tsx",
    ".html", ".css", ".scss", ".sass",
    ".json", ".xml",
    ".yml", ".yaml",
    ".kt", ".go", ".rs", ".rb", ".php",
    ".sh", ".bat", ".ps1", ".cmd",
    ".dll", ".exe", ".msi", ".sys",
    ".iso", ".img",
    ".class", ".jar",       # Java compiled
    ".pyc", ".pyo",         # Python compiled
    ".o", ".obj", ".lib",   # C/C++ compiled
    ".lock",                # package-lock, yarn.lock, etc.
    ".map",                 # source maps
    ".log"                  # logs
}

# Exact filenames to handle specially (do not skip)
PRIVATE_FILENAMES = {
    ".env"
}

# Folders to skip
SKIP_FOLDERS = {
    "$Recycle.Bin",
    "Windows",
    "Program Files",
    "Program Files (x86)",
    "ProgramData",
    "node_modules",
    "__pycache__",
    ".git",
    ".gradle",
    ".m2",
    "venv",
    ".venv",
    "env",
    ".next",
    "dist",
    "build",
    "target",           # Maven/Cargo build output
    ".idea",            # JetBrains project files
    ".vs",              # Visual Studio
    "coverage",
    ".pytest_cache"
}

# Safe extensions to MOVE instead of COPY
SAFE_TO_MOVE = {
    ".pdf"
}

# Max file size = 500 MB
MAX_FILE_SIZE = 500 * 1024 * 1024

# Scan locations
SCAN_LOCATIONS = [
    HOME / "Desktop",
    HOME / "Documents",
    HOME / "Downloads",
    HOME / "Pictures",
    HOME / "Videos",
    HOME / "Music"
]

STATS = {
    "copied": 0,
    "moved": 0,
    "skipped": 0,
    "errors": 0
}

def setup_backup_structure():
    BACKUP_ROOT.mkdir(parents=True, exist_ok=True)

    category_names = list(CATEGORIES.keys()) + [
        "Others",
        "PRIVATE"
    ]

    for category in category_names:
        (BACKUP_ROOT / category).mkdir(exist_ok=True)

    print(f"\n[+] Backup folder created:")
    print(BACKUP_ROOT)

def get_category(extension):
    extension = extension.lower()

    for category, extensions in CATEGORIES.items():
        if extension in extensions:
            return category

    return "Others"

def should_skip(path_string):
    lower_path = path_string.lower()

    for folder in SKIP_FOLDERS:
        if folder.lower() in lower_path:
            return True

    return False

def generate_destination_path(destination_folder, file_path):
    destination = destination_folder / file_path.name
    counter = 1

    while destination.exists():
        destination = (
            destination_folder /
            f"{file_path.stem}_{counter}{file_path.suffix}"
        )
        counter += 1

    return destination

# BACKUP .env FILE TO PRIVATE
# (saved as: PRIVATE/env_files/parentfolder___.env)

def backup_env_file(file_path):
    try:
        private_env_folder = BACKUP_ROOT / "PRIVATE" / "env_files"
        private_env_folder.mkdir(exist_ok=True)

        # Parent folder name as prefix so you know which project it belongs to
        parent_name = file_path.parent.name
        dest_name = f"{parent_name}__{file_path.name}"

        destination = private_env_folder / dest_name

        counter = 1
        while destination.exists():
            destination = private_env_folder / f"{parent_name}__{file_path.stem}_{counter}{file_path.suffix}"
            counter += 1

        shutil.copy2(str(file_path), str(destination))

        STATS["copied"] += 1
        print(f"[PRIVATE .env] {file_path}  ->  {dest_name}")

    except Exception as e:
        STATS["errors"] += 1
        print(f"[ENV ERROR] {file_path}")
        print(f"            {e}")

def process_file(file_path):
    try:
        if BACKUP_ROOT in file_path.parents:
            return

        if not file_path.exists():
            return
        
        if file_path.name in PRIVATE_FILENAMES:
            backup_env_file(file_path)
            return

        extension = file_path.suffix.lower()

        if extension in SKIP_EXTENSIONS:
            STATS["skipped"] += 1
            return

        try:
            file_size = file_path.stat().st_size

            if file_size > MAX_FILE_SIZE:
                print(f"[SKIP LARGE FILE] {file_path}")
                STATS["skipped"] += 1
                return

        except:
            pass

        category = get_category(extension)

        destination_folder = BACKUP_ROOT / category

        destination_path = generate_destination_path(
            destination_folder,
            file_path
        )

        if extension in SAFE_TO_MOVE:
            shutil.move(
                str(file_path),
                str(destination_path)
            )

            STATS["moved"] += 1
            print(f"[MOVE] {file_path}")

        else:
            shutil.copy2(
                str(file_path),
                str(destination_path)
            )

            STATS["copied"] += 1
            print(f"[COPY] {file_path}")

    except Exception as e:
        STATS["errors"] += 1
        print(f"[ERROR] {file_path}")
        print(f"        {e}")


def backup_private_files():
    private_folder = BACKUP_ROOT / "PRIVATE"

    ssh_path = HOME / ".ssh"

    try:
        if ssh_path.exists():
            destination = private_folder / ".ssh"

            shutil.copytree(
                ssh_path,
                destination,
                dirs_exist_ok=True
            )

            print("[PRIVATE] SSH keys backed up")

    except Exception as e:
        print(f"[SSH ERROR] {e}")

    gitconfig = HOME / ".gitconfig"

    try:
        if gitconfig.exists():
            shutil.copy2(
                gitconfig,
                private_folder
            )

            print("[PRIVATE] .gitconfig backed up")

    except Exception as e:
        print(f"[GITCONFIG ERROR] {e}")

    shell_configs = [
        ".bashrc", ".zshrc",
        ".bash_profile", ".profile",
        ".bash_aliases", ".zprofile"
    ]

    shell_dest = private_folder / "shell_configs"
    shell_dest.mkdir(exist_ok=True)

    for config_name in shell_configs:
        config_path = HOME / config_name
        try:
            if config_path.exists():
                shutil.copy2(config_path, shell_dest)
                print(f"[PRIVATE] {config_name} backed up")
        except Exception as e:
            print(f"[SHELL CONFIG ERROR] {config_name}: {e}")

    vscode_user = (
        HOME /
        "AppData" /
        "Roaming" /
        "Code" /
        "User"
    )

    try:
        if vscode_user.exists():
            vscode_destination = (
                private_folder /
                "VSCode_User"
            )

            vscode_destination.mkdir(
                exist_ok=True
            )

            important_files = [
                "settings.json",
                "keybindings.json"
            ]

            for file_name in important_files:

                source = vscode_user / file_name

                if source.exists():

                    shutil.copy2(
                        source,
                        vscode_destination
                    )

            snippets = vscode_user / "snippets"

            if snippets.exists():
                shutil.copytree(
                    snippets,
                    vscode_destination / "snippets",
                    dirs_exist_ok=True
                )

            print("[PRIVATE] VSCode settings backed up")

    except Exception as e:
        print(f"[VSCODE ERROR] {e}")

    browser_profiles = {
        "Chrome": HOME / "AppData" / "Local" / "Google" / "Chrome" / "User Data" / "Default",
        "Edge":   HOME / "AppData" / "Local" / "Microsoft" / "Edge" / "User Data" / "Default",
        "Firefox": HOME / "AppData" / "Roaming" / "Mozilla" / "Firefox" / "Profiles",
        "Brave":  HOME / "AppData" / "Local" / "BraveSoftware" / "Brave-Browser" / "User Data" / "Default",
    }

    bookmarks_dest = private_folder / "Browser_Bookmarks"
    bookmarks_dest.mkdir(exist_ok=True)

    for browser_name, profile_path in browser_profiles.items():
        bookmarks_file = profile_path / "Bookmarks"
        try:
            if bookmarks_file.exists():
                shutil.copy2(
                    bookmarks_file,
                    bookmarks_dest / f"{browser_name}_Bookmarks.json"
                )
                print(f"[PRIVATE] {browser_name} bookmarks backed up")
        except Exception as e:
            print(f"[BOOKMARKS ERROR] {browser_name}: {e}")


    gpg_path = HOME / "AppData" / "Roaming" / "gnupg"
    try:
        if gpg_path.exists():
            shutil.copytree(
                gpg_path,
                private_folder / "gnupg",
                dirs_exist_ok=True
            )

            print("[PRIVATE] GPG keys backed up")

    except Exception as e:
        print(f"[GPG ERROR] {e}")

def deep_scan():
    for location in SCAN_LOCATIONS:
        if not location.exists():
            continue

        print(f"\n[SCANNING] {location}")

        for root, dirs, files in os.walk(location):
            dirs[:] = [
                d for d in dirs
                if not should_skip(
                    os.path.join(root, d)
                )
            ]

            if should_skip(root):
                continue

            for file_name in files:
                full_path = Path(root) / file_name
                process_file(full_path)


# Scans for files > 500 MB and writes a report.
# Run this separately BEFORE the main backup to decide
# which large files you want to manually move.

def scan_large_files():
    print("\n[LARGE FILE SCAN STARTED]")
    print(f"Threshold: {MAX_FILE_SIZE // (1024 * 1024)} MB\n")

    large_files = []

    for location in SCAN_LOCATIONS:
        if not location.exists():
            continue

        for root, dirs, files in os.walk(location):
            dirs[:] = [
                d for d in dirs
                if not should_skip(os.path.join(root, d))
            ]

            if should_skip(root):
                continue

            for file_name in files:
                full_path = Path(root) / file_name

                if BACKUP_ROOT in full_path.parents:
                    continue

                try:
                    size = full_path.stat().st_size

                    if size > MAX_FILE_SIZE:
                        large_files.append((full_path, size))

                except Exception:
                    continue

    if not large_files:
        print("No files above the size limit found.")
        return

    large_files.sort(key=lambda x: x[1], reverse=True)

    print(f"{'SIZE':>10}   PATH")
    print("-" * 80)

    for file_path, size in large_files:
        size_mb = size / (1024 * 1024)
        print(f"{size_mb:>9.1f}M   {file_path}")

    report_path = HOME / "Desktop" / "large_files_report.txt"

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("LARGE FILES REPORT\n")
        f.write(f"Files above {MAX_FILE_SIZE // (1024 * 1024)} MB\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"{'SIZE (MB)':>12}   PATH\n")
        f.write("-" * 80 + "\n")

        for file_path, size in large_files:
            size_mb = size / (1024 * 1024)
            f.write(f"{size_mb:>11.1f}   {file_path}\n")

        f.write("\n" + "=" * 80 + "\n")
        f.write(f"Total large files found: {len(large_files)}\n")

    print(f"\n[+] Report saved to: {report_path}")
    print(f"[+] Total large files found: {len(large_files)}")
    print("\nReview the report, then manually copy or move")
    print("the ones you want to keep into your backup folder.")


def print_summary():

    print("\n" + "=" * 60)
    print("BACKUP SUMMARY")
    print("=" * 60)

    print(f"Copied Files : {STATS['copied']}")
    print(f"Moved Files  : {STATS['moved']}")
    print(f"Skipped Files: {STATS['skipped']}")
    print(f"Errors       : {STATS['errors']}")

    print("\nBackup Location:")
    print(BACKUP_ROOT)

if __name__ == "__main__":
    
    import sys

    if "--scan-large" in sys.argv:

        print("=" * 60)
        print("LARGE FILE SCANNER")
        print("=" * 60)

        scan_large_files()
    
    else:
        print("=" * 60)
        print("WINDOWS TO LINUX BACKUP ORGANIZER")
        print("=" * 60)

        setup_backup_structure()

        backup_private_files()

        deep_scan()

        print_summary()

        print("\n[DONE]")