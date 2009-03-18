import os, sys

def get_archive_dir(path):
    if not path.endswith('/'):
        path += '/'
    archive_dir = os.path.dirname(path)
    if not os.path.exists(os.path.join(archive_dir, 'deploy.cfg')):
        dirs = [d for d in os.listdir(archive_dir) if os.path.isdir(os.path.join(archive_dir, d))]
        if len(dirs) == 1:
            return os.path.join(archive_dir, dirs[0])
    else:
        return archive_dir
