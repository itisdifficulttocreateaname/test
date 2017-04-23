#!/usr/bin/python
#coding: utf-8

import math
import csv
from anytree import Node, RenderTree, AsciiStyle
from anytree.dotexport import RenderTreeGraph
from Radius_Change import Mark_Derivative


class NeuronNode(Node):
	def __init__(self, id, type, x, y, z, r, pid):
		super(Node, self).__init__()
		self.name = id
		self.id = id
		self.type = int(type)
		self.x = float(x) * 0.0884
		self.y = float(y) * 0.0884
		self.z = float(z) 
		self.r = float(r) * 2 #* 0.0884
		self.pid = pid

		self.parent = None
		self.branch_node_num = 0
		self.dist_to_root = 0
		self.dist_to_leaf = 0
		self.der = None


def stretch_type(list):
	m, M = min(list), max(list)
	def f(x):
		return int((x-m)/(M-m)*255)
	return f


def readSWCFile(filename):
	with open(filename, 'r') as f:
		return (line for line in f.readlines() if not line.startswith('#'))


def d(n1, n2):
	return math.sqrt((n1.x - n2.x)**2 + (n1.y - n2.y)**2 + (n1.z - n2.z)**2)


def parseLine(line):
	return NeuronNode(*line.split())


def process(tree):
	if tree.is_root:
		tree.branch_node_num = 0
		tree.dist_to_root = 0
	else:
		tree.dist_to_root = tree.parent.dist_to_root + d(tree, tree.parent)
		if not tree.parent.is_root and len(tree.siblings) > 0:
			tree.branch_node_num = tree.parent.branch_node_num + 1
		else:
			tree.branch_node_num = tree.parent.branch_node_num
	
	for child in tree.children:
		process(child)
	else:
		if tree.is_leaf:
			tree.dist_to_leaf = 0
			Mark_Derivative(tree)

		else:
			dists = ((d(tree, child) + child.dist_to_leaf) for child in tree.children)
			tree.dist_to_leaf = min(dists)


def createForest(swc):
	all_node = {}
	forest = []
	for line in swc:
		node = parseLine(line) 
		all_node[node.name] = node
		if node.pid == '-1':
			forest.append(node)
		else:
			node.parent = all_node[node.pid]

	for tree in forest:
		process(tree)
		nodes = (tree, )+tree.descendants
		
		f = stretch_type([node.der for node in nodes])
		for node in nodes:
			node.type = f(node.der)
		
	return forest


def print_tree_to_CSVFile(tree, spamwriter):
	spamwriter.writerow([tree.id, tree.type, tree.r/2*0.0884, tree.der, tree.branch_node_num, tree.dist_to_root, tree.dist_to_leaf])
	for child in tree.children:
		print_tree_to_CSVFile(child, spamwriter)


def print_forest_to_CSVFile(forest, filename):
	with open(filename, 'wb') as csvfile:
		spamwriter = csv.writer(csvfile, delimiter = ',', quotechar = '|', quoting = csv.QUOTE_MINIMAL)
		spamwriter.writerow(['Id', 'Type', 'Raius', 'Sec-order Der',  '#branch_points', 'Dist_to_root', 'Dist_to_leaf'])
		for tree in forest:
			print_tree_to_CSVFile(tree, spamwriter)


def print_forest_to_SWCFile(forest, filename):
	with open(filename, 'wb') as swcfile:
		swcfile.write('# Id, Type, x, y, z, Radius, Parent\n')
		for tree in forest:
			nodes = (tree, ) + tree.descendants
			for node in nodes:
				swcfile.write('{0}, {1}, {2}, {3}, {4}, {5}, {6}\n'.format(node.id, node.type, node.x, node.y, node.z, node.r/2*0.0884, node.pid))
		swcfile.flush()


if __name__ == '__main__':
	swc = readSWCFile('test.swc')
	forest = createForest(swc)
	print_forest_to_CSVFile(forest, 'Node_Info.csv')
	print_forest_to_SWCFile(forest, 'After_stretch.swc')
