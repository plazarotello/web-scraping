import os, shutil

def create_directory(dir_name : str):
    if os.path.exists(dir_name) and os.path.isdir(dir_name):
        shutil.rmtree(dir_name)
    os.mkdir(dir_name)

def create_file(dir : str, file_name : str):
    return open(os.path.join(dir, file_name), 'w+')