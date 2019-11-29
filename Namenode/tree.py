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

    def add_file(self, name, path, size, storage):
        new_file = File(name, path, size, storage, self)
        self.files.append(new_file)
        return new_file
    
    def replicate(self, name):
        for i in self.files:
            if i.name == name:
                print('Found ' + i.name)
    
    def get_path_entity(self, path):
        path_array = path.split("/")[1:]
        current = self
        for j in path_array:
            for i in current.dirs:
                print(i.name)
                if i.name == j:
                    current = i
                    break
                else:
                    continue
        return current

    def delete_file(self, name):
        deleted = 0
        for i in self.files:
            if i.name == name:
                self.files.remove(i)
                deleted = 1
                break
        if deleted == 1:
            print("File was deleted")
        else:
            print('File to be deleted does not exist:', name)


class File:

    def __init__(self, name, path, size, storages, parent=None):
        self.parent = parent
        self.name = name
        self.path = path
        self.size = size
        self.last_mod = datetime.datetime.now().ctime()
        self.storages = storages

    def info(self):
        info = 'Name: ' + str(self.name) + '\n' + 'Size: ' + str(self.size) + ' bytes' + '\n' + 'Path: ' + \
               str(self.path) + '\n' + 'Modified: ' + str(self.last_mod)
        return info

storages = []

root = Tree('root', '/')
root.add_dir('n1', '/n1')
root.add_dir('n2', '/n2')
node_2 = root.get_path_entity('/n2')
node_1 = root.get_path_entity('/n1')
node_2.add_file('first', '/first.txt', 70614, 'n2')
print(node_1.files)
#root.replicate('first')
#print(root.files[0].info())
