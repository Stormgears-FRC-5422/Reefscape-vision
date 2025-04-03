import os
import random
import string
from shutil import copy2
import stat

def print2log(*argv, folder=""):
    string1 = " ".join([str(arg) for arg in argv])

    # for arg in argv:
    #     string1 += str(arg)
    string1 += "\n"
    # print(string1)
    if len(folder) == 0:
        file = "all.log"
    else:
        file = os.path.join(folder, "all.log")
    try:
        with open(file,"a") as fout:
            fout.write(string1)
    except Exception:
        pass


def print2log1(*argv, folder=""):
    string1 = " ".join([str(arg) for arg in argv])

    # for arg in argv:
    #     string1 += str(arg)
    string1 += "\n"
    print(string1)
    if len(folder) == 0:
        file = "all.log"
    else:
        file = os.path.join(folder, "all.log")
    try:
        with open(file,"a") as fout:
            fout.write(string1)
    except Exception:
        print(f"Warning: Failed to write to all.log")


def create_random_dir(parent_dir):
    parent_dir = parent_dir
    length = 8
    while True:
        random_folder = ''.join(random.choices(string.ascii_letters +
                                               string.digits, k=length))
        random_path = os.path.join(parent_dir, random_folder)
        if os.path.isdir(random_path) or os.path.isfile(random_path):
            pass
        else:
            os.makedirs(random_path, exist_ok=False)
            break
    return random_path

def create_sequential_dir(parent_dir):
    if os.path.isdir(parent_dir):
        parent_dir = parent_dir
        length = 8
        folders = os.listdir(parent_dir)
        i = 0
        leading_char = [folder[0:4] for folder in folders]
        while True:
            if f"{i:03d}_" in leading_char:
                i += 1
                continue
            else:
                new_folder = f"{i:03d}_" + ''.join(random.choices(
                    string.ascii_letters + string.digits, k=length))
                break

        new_path = os.path.join(parent_dir, new_folder)
        os.makedirs(new_path, exist_ok=False)
    else:
        new_path = ""

    return new_path

def backup_file(src_path, dest_dir):
    if os.path.isfile(src_path):
        os.makedirs(dest_dir, exist_ok=True)

        length = 8
        _, filename = os.path.split(src_path)
        name, extension = os.path.splitext(filename)

        while True:
            random_name = name + ''.join(random.choices(string.ascii_letters +
                                                   string.digits, k=length))
            random_path = os.path.join(dest_dir, random_name + extension)
            if os.path.isfile(random_path):
                pass
            else:
                break

        try:
            copy2(src_path, random_path)
            return True, random_path
        except Exception as e:
            print(f"An error occurred: {e}")
            return False, random_path
    else:
        return True, ""


def is_directory_read_only(directory_path):
    """
    Checks if a directory is read-only.

    Args:
        directory_path: The path to the directory.

    Returns:
        True if the directory is read-only, False otherwise.
    """
    try:
        # Get the file permissions
        permissions = os.stat(directory_path).st_mode
        # Check if write permissions are denied for the owner, group, and others
        return not (permissions & stat.S_IWUSR or permissions & stat.S_IWGRP or permissions & stat.S_IWOTH)
    except FileNotFoundError:
        return False  # Directory doesn't exist, consider it not read-only
    except Exception as e:
         print(f"An error occurred: {e}")
         return False

def is_directory_writable(path):
    """
    Checks if a directory is writable.

    Args:
    path: The path to the directory.

    Returns:
    True if the directory is writable, False otherwise.
    """
    if os.path.isdir(path):
        print2log(f"Directory {path} exist - is_directory_writable()")
        return os.access(path, os.W_OK)
    else:
        try:
            print2log(f"creating Directory {path} - is_directory_writable()")
            os.makedirs(path, exist_ok=True)
            return os.access(path, os.W_OK)
        except Exception:
            print2log(f"Failed to create folder {path} - is_directory_writable()")
            return False

if __name__ == "__main__":
    create_sequential_dir(r"F:\_temp\_temp4")
