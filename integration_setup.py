# Script to integrate pattern engine into Django app

import os
import shutil


def setup_pattern_engine():
    """
    Set up the pattern engine integration by copying the existing code
    into the Django app structure.
    """
    # Source directories (replace with your actual code path)
    src_dir = "src"

    # Destination directory in Django app
    dest_dir = "patterns/pattern_engine"

    # Ensure destination directory exists
    os.makedirs(dest_dir, exist_ok=True)

    # Create an __init__.py file in the destination directory
    with open(os.path.join(dest_dir, "__init__.py"), "w") as f:
        f.write("# Pattern engine module\n")

    # Copy all the Python files from source to destination
    for root, dirs, files in os.walk(src_dir):
        # Create corresponding subdirectory in destination
        rel_path = os.path.relpath(root, src_dir)
        dest_subdir = os.path.join(dest_dir, rel_path) if rel_path != "." else dest_dir
        os.makedirs(dest_subdir, exist_ok=True)

        # Create __init__.py in each subdirectory
        if not os.path.exists(os.path.join(dest_subdir, "__init__.py")):
            with open(os.path.join(dest_subdir, "__init__.py"), "w") as f:
                f.write(f"# Pattern engine {rel_path} module\n")

        # Copy Python files
        for file in files:
            if file.endswith(".py") and file != "__init__.py":
                src_file = os.path.join(root, file)
                dest_file = os.path.join(dest_subdir, file)
                shutil.copy2(src_file, dest_file)
                print(f"Copied: {src_file} -> {dest_file}")


if __name__ == "__main__":
    setup_pattern_engine()