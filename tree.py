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
        self.storage_nodes = []

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
            if i.name == name:
                self.files.remove(i)
                break
        print('File to be deleted is not exist:', name)


class File:

    def __init__(self, name, path, size, parent=None):
        self.parent = parent
        self.name = name
        self.path = path
        self.size = size
        self.last_mod = datetime.datetime.now().ctime()
        self.storg_nodes = []

    def info(self):
        info = 'Name: ' + str(self.name) + '\n' + 'Size: ' + str(self.size) + ' bytes' + '\n' + 'Path: ' + \
               str(self.path) + '\n' + 'Modified: ' + str(self.last_mod)
        return info


root = Tree('root', '/')
root.add_dir('b1', '/b1')
root.add_dir('b2', '/b2')
root.add_file('first', '/first.txt', 70614)
root.delete_file('firstt')
print(root.files[0].info())
