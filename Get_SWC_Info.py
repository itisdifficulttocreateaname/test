#!/usr/bin/python
#-*-coding=utf-8-*-


class Node(object):

	def __init__(self, index, type, x, y, z, radius, pid): #x、y、z：为了读入的数据能直接导入
		self.index = index
		self.type = type
		self.x = x
		self.y = y
		self.z = z
		self.radius = radius
		self.pid = pid

		self.parent = None # parent NODE
		self.depth = 0
		self.branch_node_num = 0
		self.path_to_ending = 0 
		self.children = [] # ************

def readSWCFile(filename): # file => data tuple
	with open(filename, 'r') as f:
		return (line for line in f.readlines() if not line.startswith('#')) # return a tuple not a list

def parseLine(line): # line => node (as str type)
	return Node(*line.split()) # !!!!!

def process(tree): # to caldulate "branch_node_num" & "path_to_ending" for each node.
	if not tree.parent: # has no parent i.e. the root
		tree.branch_node_num = 0
	elif tree.parent.pid != '-1' and len(tree.parent.children) > 1: # parent is a branch point and not the root
		tree.branch_node_num = tree.parent.branch_node_num + 1
	else:
		tree.branch_node_num = tree.parent.branch_node_num

	for child in tree.children:
		process(child)

		##### By now, #{branch points} of all node has been calculated.
		##### The following part is to calculate the distance 
		##### from each node to its corresponding ending point.

	else:
		if not tree.children: # has no child i.e. the ending node
			tree.path_to_ending = 0
		else:
			tree.path_to_ending = 1 + min(c.path_to_ending for c in tree.children)

def createForest(swc): 
	all_node = {}  # ******************* TO FIND EACH NODE IN ORDER TO CONSTRUCT STRCTURE
	forest = []
	for line in swc: # construct the structure of trees
		node = parseLine(line)
		if node.pid == '-1': # if the root, put into forest
			forest.append(node)
		else: # self.parent, self.depth, self.children
			parent_node = all_node[node.pid]
			node.parent = parent_node
			node.depth = node.parent.depth + 1
			node.parent.children.append(node)
		all_node[node.index] = node

	for tree in forest: # complete all indirect information of each node
		process(tree)
	return forest

def print_tree(tree):
	f.writelines(str(tree.index) + '    ' + str(tree.radius) + '    ' + str(tree.depth) + '    ' + str(tree.branch_node_num) + '    ' + str(tree.path_to_ending) + '\n')
	for c in tree.children:
		print_tree(c)

if __name__ == '__main__':
	swc = readSWCFile('test.swc')
	forest = createForest(swc)
	with open('Neuron_Info.txt', 'w') as f:
		f.writelines('id  radius  depth  num_of_branch_points  distance_to_end_point\n')
		for tree in forest:
			print_tree(tree)
	


