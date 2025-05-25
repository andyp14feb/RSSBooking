#
#  
# https://github.com/andyp14feb/treepy
#
#
#!/usr/bin/env python3
import os
import sys
import argparse

SPACE = "    "
BRANCH = "│   "
TEE    = "├── "
LAST   = "└── "

# Folder dan file yang akan diabaikan
IGNORED_DIRS = {'__pycache__', '.git', '.venv', 'node_modules', '.mypy_cache', '.idea', '.vscode'}
IGNORED_FILES = {'.DS_Store', 'Thumbs.db'}
IGNORED_EXTENSIONS = {'.pyc', '.pyo', '.log', '.tmp', '.bak'}

def is_ignored(name, full_path):
    # Abaikan folder tertentu
    if os.path.isdir(full_path) and name in IGNORED_DIRS:
        return True
    # Abaikan file tertentu
    if os.path.isfile(full_path):
        if name in IGNORED_FILES:
            return True
        _, ext = os.path.splitext(name)
        if ext.lower() in IGNORED_EXTENSIONS:
            return True
    return False

def tree_to_file(dir_path, prefix="", file=None):
    entries = sorted(
        [e for e in os.listdir(dir_path) if not is_ignored(e, os.path.join(dir_path, e))],
        key=lambda x: (not os.path.isdir(os.path.join(dir_path, x)), x.lower())
    )
    for index, name in enumerate(entries):
        path = os.path.join(dir_path, name)
        connector = LAST if index == len(entries) - 1 else TEE
        file.write(f"{prefix}{connector}{name}\n")
        if os.path.isdir(path):
            extension = SPACE if index == len(entries) - 1 else BRANCH
            tree_to_file(path, prefix + extension, file=file)

def main():
    parser = argparse.ArgumentParser(description="Save folder tree to structure.txt (ignoring temporary files)")
    parser.add_argument("folder", nargs="?", default=".", help="Root folder (default: current directory)")
    args = parser.parse_args()

    root = os.path.abspath(args.folder)
    with open("structure.txt", "w", encoding="utf-8") as f:
        f.write(os.path.basename(root) + "/\n")
        tree_to_file(root, file=f)

if __name__ == "__main__":
    main()
