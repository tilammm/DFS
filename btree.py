from treelib import Node, Tree

def add_user(user_name, current_tree):
	current_tree.create_node(user_name, user_name, parent = "fs")
	return current_tree

def restore_path(current_tree, dir):
	dir = dir.split('/')
	for i in range(len(dir)-1):
		if current_tree.get_node(dir[i]):
			print(dir[i] + "is found")
			continue
		else:
			current_tree.create_node(dir[i], dir[i], parent=dir[i-1])
	return current_tree

#def add_file(where_to, filename): 
def add_node_loc(current_tree, dir_name):

	dir_name = dir_name.split('/')
	node = current_tree.get_node(dir_name[-1])

	print(node)
	if(node):
		print("Found it at the tree")
	else:
		current_tree.create_node(dir_name[-1], dir_name[-1], parent = dir_name[-2])
	return current_tree


if __name__ == '__main__':

	general_tree = Tree()
	general_tree.create_node("File system", "fs")
	general_tree = add_user("Mark", general_tree)
	general_tree = add_user("Askar", general_tree)
	general_tree = restore_path(general_tree, "Mark/Test/text.txt")
	general_tree.show()
	general_tree = add_node_loc(general_tree, "Mark/text.txt")
	general_tree = add_node_loc(general_tree, "Mark/Test/text.txt")
	general_tree.show()
	print(general_tree)


	#placeholder id
	