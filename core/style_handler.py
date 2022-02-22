import os

def current_file_path():
    '''Get path of current file
    '''
    return str(os.path.dirname(os.path.realpath(__file__)).replace("\\","/"))

def icon_path(icon_name=str(), icon_format=str("png")):
    '''Get icon path
    '''
    return os.path.normpath("{0}/icons/{1}.{2}".format(current_file_path(),icon_name,icon_format))