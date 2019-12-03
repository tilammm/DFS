import datetime


def swap_ip(file, ip, ips_of_storages):
    for storage in file.storages:
        if storage != ip:
            result_storage = storage
    for node in ips_of_storages:
        if node != result_storage and node != ip:
            new_ip = node

    file.storages = [result_storage, new_ip]
    return file, result_storage


class Tree:

    def __init__(self, name, path, dirs=None, files=None, parent=None):
        self.parent = parent
        self.files = files or []
        self.dirs = dirs or []
        self.name = name
        self.path = path
        self.created = datetime.datetime.now().ctime()

    def delete_dir(self):
        if self.parent is None:
            return 'error'
        for file in self.files:
            del file
        for child in self.dirs:
            child.delete_dir()
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
    
    def get_path_entity(self, path):
        path_array = path.split("/")
        current = self
        for j in path_array:
            for i in current.dirs:
                if i.name == j:
                    current = i
                    break
        if current.path == path or current.path[:len(current.path) - 1] == path:
            return current
        else:
            return None

    def delete_file(self, name):
        result = 'can not delete file'
        for file in self.files:
            if file.name == name:
                self.files.remove(file)
                result = 'ok'
                del file
                break
        return result

    def get_file(self, name):
        for file in self.files:
            if file.name == name:
                return file
        return None

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

    def replicate(self, ip, storage_nodes):
        list_of_ip = []
        for node in storage_nodes:
            list_of_ip.append(node[0])
        result = []
        for index in range(len(self.files)):
            if ip in self.files[index].storages:
                self.files[index], result_ip = swap_ip(self.files[index], ip, list_of_ip)
                result.append((self.files[index].path, result_ip))
        for index in range(len(self.dirs)):
            result.append(self.dirs[index].replicate(ip, storage_nodes))
        return result

    def size_of_dir(self, storage_nodes):
        list_of_ip = []
        for node in storage_nodes:
            list_of_ip.append(node[0])
        result = [0, 0, 0]
        for file in self.files:
            for i, node in enumerate(list_of_ip):
                if node in file.storages:
                    result[i] += int(file.size)
        for child in self.dirs:
            subresult = child.size_of_dir()
            for i in range(3):
                result[i] += subresult[i]
        return result[0], result[1], result[2]


class File:

    def __init__(self, name, path, size=0, storages=[], parent=None):
        self.parent = parent
        self.name = name
        self.path = path
        self.size = size
        self.created = datetime.datetime.now().ctime()
        self.storages = storages

    def info(self):
        info = 'Name: ' + str(self.name) + '\n' + 'Size: ' + str(self.size) + ' bytes' + '\n' + 'Path: ' + \
               str(self.path) + '\n' + 'Created: ' + str(self.created)
        return info

