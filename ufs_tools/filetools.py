import os
import time
import random
import re
import logging
# The following codes are copied from
# http://stackoverflow.com/questions/606561/how-to-get-filename-of-the-main-module-in-python
import imp
import sys

from folder_tool import find_root, find_root_path
from file_search import find_filename_in_folder, find_filename_with_pattern_in_folder


def main_is_frozen():
    return (hasattr(sys, "frozen") or  # new py2exe
            hasattr(sys, "importers") or  # old py2exe
            imp.is_frozen("__main__"))  # tools/freeze


def get_main_exec():
    if main_is_frozen():
        # print 'Running from path', os.path.dirname(sys.executable)
        return sys.executable
    return sys.argv[0]


def get_main_exec_path():
    dir_path = os.path.abspath(os.path.dirname(get_main_exec()))
    return dir_path


def get_main_file():
    # print "----------------------", get_main_exec()
    # find path to where we are running
    return os.path.basename(get_main_exec()).split(".")[0]


def get_free_file_name(path, nameWithoutExt, ext):
    path_without_ext = os.path.join(path, nameWithoutExt)
    while os.path.exists(path_without_ext + ext):
        path_without_ext += '-' + str(random.randint(0, 10))
        # print thumb_path_without_ext
    return path_without_ext + ext


def get_free_name_from_full_path(full_path):
    """
    Just give a full path like: d:/good/bad.txt, generate a new path with a number in it and will not conflict with
    the files in that path. such as d:/good/bad-5.txt
    :param full_path:
    :return:
    """
    path = os.path.dirname(full_path)
    ext = os.path.splitext(full_path)[1]
    basename = os.path.basename(full_path)
    # print basename
    name_without_ext = basename[0:-(len(ext))]
    # print name_without_ext
    if name_without_ext == '':
        name_without_ext = basename
        ext = ''
    res = get_free_file_name(path, name_without_ext, ext)
    # print res
    return res


def get_free_timestamp_filename_in_path(path, dot_ext, prefix=''):
    """
    Return a unused filename according to current time.
    :param path:
    :param ext: should start with "."
    :param prefix:
    :return:
    """
    # print path, ext, prefix
    filename = unicode(prefix + str(time.time()))
    return get_free_file_name(path, filename, dot_ext)


def find_file_in_product(filename):
    p = os.getcwd()
    return find_filename_in_folder(p, filename)


def find_filename_in_app_framework_with_pattern(pattern):
    p = os.getcwd()
    return find_filename_with_pattern_in_folder(p, pattern)


def find_callable_in_app_framework(filename):
    # filename = filename.replace('-', '\-')
    return find_filename_in_app_framework_with_pattern('^' + filename + "((\.bat$)|(\.py$)|(\.exe$)|(\.com$))")


log = logging.getLogger(__name__)


def collect_files_in_dir(file_root_full_path, ext=None, ignore_file_list=[]):
    res = []
    if os.path.exists(file_root_full_path) and os.path.isdir(file_root_full_path):
        # log.error(file_root_full_path)
        for filename in os.listdir(file_root_full_path):
            # log.error(filename)
            if filename in ignore_file_list:
                # print "ignoring: ", filename
                continue
            if (ext is None) or (ext in filename):
                # To ensure .pyc is not included
                if len(filename.split(ext)[1]) != 0:
                    continue
                full_path = os.path.join(file_root_full_path, filename)
                # print full_path
                res.append(full_path)
    return res


def get_app_name_from_full_path(app_path):
    app_filename = os.path.basename(app_path)
    app_name = app_filename.split(".")[0]
    return app_name


def get_folder(file_path):
    return os.path.abspath(os.path.dirname(file_path))


def get_parent_folder(file_path):
    # print "parent:"+os.path.abspath(os.path.join(os.path.dirname(file_path),".."))
    return os.path.abspath(os.path.join(os.path.dirname(file_path), ".."))


def get_sibling_folder(file_path, folder_name):
    return os.path.abspath(os.path.join(get_folder(file_path), folder_name))


def find_root_even_frozen(root_name):
    if main_is_frozen():
        # log.error("frozen, "+find_root_path(sys.executable, root_name))
        return find_root_path(sys.executable, root_name)
    else:
        # log.error(dir(sys))
        return find_root(root_name, 2)


g_local_string_encoding = 'gb2312'


def translate_local_string_to_unicode(original_str):
    """
    Transform a string in local format to unicode. This may be changed in different
    system as different system has different default encoding
    """
    if type(original_str) != unicode:
        return original_str.decode(g_local_string_encoding)
    return original_str


def format_path(original_dir):
    """
    Transform dir to internal format.
    In windows, it will be like: D:/helloworld.txt
      The driver letter D should be capitalized. Separator should be '/' instead of '\\'

    The input should be unicode. Anyway, we'll check it in this function.

    """
    if original_dir is None:
        raise "tried to transform None to standard path"
    # if isUfsUrl(original_dir):
    #    raise "is ufs url, not path"
    new_dir = translate_local_string_to_unicode(os.path.abspath(original_dir))
    # print type(new_dir)
    if sys.platform == 'win32':
        # In windows, make the driver letter upper case
        if new_dir[1] == u':':
            new_dir = new_dir[0].upper() + new_dir[1:]
        else:
            logging.error('not a correct directory format in windows. Dir is:', new_dir)
    new_dir = new_dir.replace(u'\\', u'/')
    # ncl(new_dir)
    # TODO: support linux path?
    # Remove trail '/'
    # print new_dir
    new_dir = new_dir.rstrip(u'/')
    if sys.platform == 'win32':
        # In windows, make the driver letter upper case
        if len(new_dir) == 2:
            # C: or E:
            new_dir += u"/"
    return unicode(new_dir)
