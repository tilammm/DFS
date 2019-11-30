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
        if self.parent is None:
            return 'Can not delete root directory'
        for file in self.files:
            del file
        for child in self.dirs:
            child.delete_self()
        parent = self.parent
        parent.dirs.remove(self)
        del self
        return parent

    def add_dir(self, name, path=None):
        for dir in self.dirs:
            if dir.name == name:
                return 'Directory exists'
        path = self.path + name + '/'
        new_dir = Tree(name, path, parent=self)
        self.dirs.append(new_dir)
        return 'ok'

    def add_file(self, name, size, storage):
        # correct name
        candidate = name
        duplicate = False
        for file in self.files:
            if name == file.name:
                duplicate = True
        i = 1
        while duplicate:
            duplicate = False
            index = name.rindex('.')
            candidate = name[:index] + '(Copy_' + str(i) + ')' + name[index:]
            for file in self.files:
                if candidate == file.name:
                    duplicate = True
        i += 1

        # new file to list
        path = self.path + candidate
        new_file = File(candidate, path, size, storage, self)
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
        result = 'can not delete file'
        for file in self.files:
            if file.name == name:
                self.files.remove(file)
                result = 'ok'
                del file
                break
        return result

    def get_files(self):
        result = []
        for file in self.files:
            result.append(file.name)
        return result

    def get_dirs(self):
        result = []
        for dir in self.dirs:
            result.append(dir.name)
        return result

    def open(self, name):
        for dir in self.dirs:
            if dir.name == name:
                return dir
        return None


class File:

    def __init__(self, name, path, size=0, storages=[], parent=None):
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

