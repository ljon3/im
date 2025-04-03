import os

def fullpath(*args):
    # returns os independent file path choosing the right file separator
    return os.path.join( *args )

def checkpath(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)           