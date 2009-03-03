from tarfile import is_tarfile
from os.path import join, isdir, exists

##__all__ = ['']

def create_apache_config(dest, content):
    f = file(dest, 'w').write(content)

def get_project_config(name):
    if not exists(name):
        raise Exception("'%s' No such file or directory" % name)
    elif isdir(name):
        return join(name, 'deploy.cfg')
    elif not is_tarfile(name):
        raise NotImplementedError
    else:
        raise Exception("'%s' unknow error." % name)

def extract_project(name):
    pass
