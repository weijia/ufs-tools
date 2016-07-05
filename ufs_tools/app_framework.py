import inspect
import os

import sys

from folder_tool import get_root_sub_folder, ensure_dir


class AppConfig(object):
    def __init__(self, file_path, root_name):
        self.file_path = file_path
        self.root_name = root_name

    def get_or_create_app_data_folder(self, data_folder_name):
        app_data_folder = get_root_sub_folder(self.file_path, self.root_name, "../data/%s" % data_folder_name)
        ensure_dir(app_data_folder)
        return app_data_folder

    def get_app_in_framework(self, folder, name):
        other_app_full_path = get_root_sub_folder(self.file_path, self.root_name, "../others/%s" % folder)
        full_path = os.path.join(other_app_full_path, name)
        if os.path.exists(full_path):
            return full_path
        print full_path
        raise "Not exist"


def find_app_in_folders(folder_list, app_name_ext):
    for folder in folder_list:
        if os.path.exists(os.path.join(folder, app_name_ext)):
            return folder
    raise "Not found"


def get_executable():
    """
    Get the executable position, if the application is called without path, then this function will fail.
    :return:
    """
    # print sys.argv
    # stack = inspect.stack()
    # s = stack[-1][1]
    # for i in stack:
    #     print i
    s = os.path.abspath(sys.argv[0])
    print s
    return s


def get_executable_folder():
    executable_folder = os.path.dirname(get_executable())
    if executable_folder == "":
        print "!!!!!!!!!", executable_folder
        executable_folder = os.getcwd()
    return executable_folder


if __name__ == '__main__':
    print get_executable_folder()
