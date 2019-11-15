import sys
import datetime


class Tree:

    def __init__(self, name, path, dirs=None, files=None, parent=None):
        self.parent = parent
        self.files = files or []
        self.dirs = dirs or []
        self.name = name
        self.path = path
        self.last_mod = datetime.datetime.now().ctime()
        self.number_of_file = 0
        self.storg_nodes = []

    def delete_dir(self):
        for file in self.files:
            del file
        for child in self.dirs:
            child.delete_self()
        del self

    def add_dir(self, name, path):
        new_dir = Tree(name, path, parent=self)
        self.dirs.append(new_dir)
        return new_dir

    def add_file(self, name, path, size):
        new_file = File(name, path, size, self)
        self.files.append(new_file)
        return new_file

    def delete_file(self, name):
        for i in self.files:
            if(i.name == name):
                self.files.remove(i)
                break



class File:

    def __init__(self, name, path, size, parent = None):
        self.parent = parent
        self.name = name
        self.path = path
        self.size = size
        self.last_mod = datetime.datetime.now().ctime()
        self.storg_nodes = []





root = Tree('root', '/')
root.add_dir('b1', '/b1')
root.add_dir('b2', '/b2')

