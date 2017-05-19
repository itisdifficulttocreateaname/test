#!/usr/bin/env python
#coding: utf-8

import sys
import math
import csv
from anytree import Node

from Radius_Change import PlotForest
from TreeNodes import AllTreeNodes
from TreeParaRescale import TreeParaRescale
from StretchType import Stretch_Type


class NeuronNode(Node):

    def __init__(self, id, type, x, y, z, r, pid):
        super(Node, self).__init__()
        self.name = id
        self.id = id
        self.type = int(type)
        self.x = float(x) 
        self.y = float(y) 
        self.z = float(z) 
        self.r = float(r) 
        self.pid = pid
        self.parent = None

        self.branch_node_num = 0 # not include root
        self.dist_to_root = 0
        self.dist_to_leaf = 0

        self.der = None


    def para_rescale(self, para, coe):
        if para is 'x':
            self.x *= coe
        elif para is 'y':
            self.y *= coe
        elif para is 'z':
            self.z *= coe
        elif para is 'r':
            self.r *= coe


def readSWCFile(filename):
    if not filename.lower().endswith('.swc'):
        IOError('Invalid file format: {0}'.format(filename))
    with open(filename, 'r') as f:
        return (line for line in f.readlines() if not line.startswith('#'))


def d(n1, n2):  
    return math.sqrt((n1.x - n2.x)**2 + (n1.y - n2.y)**2 + (n1.z - n2.z)**2)


def parseLine(line):
    return NeuronNode(*line.split())


def process(tree): #second section properties
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

        else:
            dists = ((d(tree, child) + child.dist_to_leaf) for child in tree.children)
            tree.dist_to_leaf = min(dists)


def createForest(swc):
    all_node = {}
    forest = []
    for line in swc: #first section properties
        node = parseLine(line) 
        all_node[node.name] = node
        if node.pid == '-1':
            forest.append(node)
        else:
            node.parent = all_node[node.pid]
    return forest


def completeForest(swc):
    forest = createForest(swc)
    for tree in forest:
        TreeParaRescale(tree, **{'x': 0.0884, 'y': 0.0884, 'r': 0.0884})
        process(tree) #second section properties

    return forest


def SWC2Forest(filename, node_type = NeuronNode):
    swc = readSWCFile(filename)
    forest = completeForest(swc)
    Stretch_Type(forest)
    return forest


def print_tree_to_CSVFile(tree, spamwriter):
    spamwriter.writerow([tree.id, tree.type, tree.r, tree.der, tree.branch_node_num, tree.dist_to_root, tree.dist_to_leaf])
    for child in tree.children:
        print_tree_to_CSVFile(child, spamwriter)


def print_forest_to_CSVFile(forest, filename):
    with open(filename, 'wb') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter = ',', quotechar = '|', quoting = csv.QUOTE_MINIMAL)
        spamwriter.writerow(['Id', 'Type', 'Raius', 'Sec-order Der',  '#branch_points', 'Dist_to_root', 'Dist_to_leaf'])
        for tree in forest:
            print_tree_to_CSVFile(tree, spamwriter)


def print_tree_to_SWCFile(tree, swcfile):
    nodes = AllTreeNodes(tree)
    for node in nodes:
        swcfile.write('{0}, {1}, {2}, {3}, {4}, {5}, {6}\n'.format(node.id, node.type, node.x, node.y, node.z, node.r, node.pid))


def print_forest_to_SWCFile(forest, filename):
    with open(filename, 'wb') as swcfile:
        swcfile.write('# Id, Type, x, y, z, Radius, Parent\n')
        for tree in forest:
            print_tree_to_SWCFile(tree, swcfile)
        swcfile.flush()


def SWC_CSVorSWC(input_swcfile, **output):
    forest = SWC2Forest(input_swcfile)
    if 'csv' in output:
        print_forest_to_CSVFile(forest, output['csv'])
    if 'swc' in output:
        print_forest_to_SWCFile(forest, output['swc'])


def main(plot = False):
    abs_path = os.path.dirname(os.path.abspath(__file__))
    testfile_path = os.path.join(abs_path, '..', 'test.swc')
    
    if plot == True:
        forest = SWC2Forest(testfile_path)
        PlotForest(forest)


if __name__ == '__main__':
    import os
    main(True)

