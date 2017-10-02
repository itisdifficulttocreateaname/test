#!/usr/bin/env python
#coding: utf-8

import sys
import math
import csv
from anytree import Node

from Radius_Change import plot_tree, PLOT_DIR
from StretchType import stretch_type
from ele_manipulation import ele_mani
from cmd import check_file
from globals import my_global

my_global = my_global()
X_RESCALE = my_global.x_rescale
Y_RESCALE = my_global.y_rescale
Z_RESCALE = my_global.z_rescale
R_RESCALE = my_global.r_rescale


# X_RESCALE = 0.0884
# Y_RESCALE = 0.0884
# Z_RESCALE = 1.0
# R_RESCALE = 0.0884

# X_RESCALE = 0.221180865682821
# Y_RESCALE = 0.221180865682821
# X_RESCALE = 0.110590432841411
# Y_RESCALE = 0.110590432841411
# Z_RESCALE = 0.7
# Z_RESCALE = 1.0
# R_RESCALE = 1.0


class NeuronNode(Node):

    def __init__(self, id, type, x, y, z, r, pid):
        super(Node, self).__init__()
        self.name = id
        self.id = id
        self.type = int(type)
        self.sd_type = int(type)
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
        self.is_der_loc_min = False

    @property
    def all_nodes(self):
        return (self.root, ) + self.root.descendants

    @property
    def all_leaves(self):
        return filter(lambda node: node.is_leaf, self.all_nodes)


    def node_para_rescale(self, **rescale):
        if 'x' in rescale:
            self.x *= rescale['x']
        if 'y' in rescale:
            self.y *= rescale['y']
        if 'z' in rescale:
            self.z *= rescale['z']
        if 'r' in rescale:
            self.r *= rescale['r']

    def tree_para_rescale(self, **rescale):
        for node in self.all_nodes:
            node.node_para_rescale(**rescale)
        

######################### SWC_FOREST ###########################

def _read_swc(filename):
    check_file(filename, 'swc')
    with open(filename, 'r') as f:
        return (line for line in f.readlines() if not line.startswith('#'))


def _d(n1, n2):  
    return math.sqrt((n1.x - n2.x)**2 + (n1.y - n2.y)**2 + (n1.z - n2.z)**2)


def _line_node(line):
    return NeuronNode(*line.split())


def _info_extract(tree): #second section properties
    if tree.is_root:
        tree.branch_node_num = 0
        tree.dist_to_root = 0
    else:
        tree.dist_to_root = tree.parent.dist_to_root + _d(tree, tree.parent)
        if not tree.parent.is_root and len(tree.siblings) > 0:
            tree.branch_node_num = tree.parent.branch_node_num + 1
        else:
            tree.branch_node_num = tree.parent.branch_node_num
    
    for child in tree.children:
        _info_extract(child)
    else:
        if tree.is_leaf:
            tree.dist_to_leaf = 0

        else:
            dists = ((_d(tree, child) + child.dist_to_leaf) for child in tree.children)
            tree.dist_to_leaf = min(dists)


def _forest_create(swc):
    all_node = {}
    forest = []
    for line in swc: #first section properties
        node = _line_node(line) 
        all_node[node.name] = node
        if node.pid == '-1':
            forest.append(node)
        else:
            node.parent = all_node[node.pid]
    return forest


def _forest_complete(swc):
    forest = _forest_create(swc)
    for tree in forest:
        tree.tree_para_rescale(x = X_RESCALE, y = Y_RESCALE, z = Z_RESCALE, r = R_RESCALE)
        _info_extract(tree) #second section properties

    return forest


def swc_forest(swc_file, node_type = NeuronNode):
    swc = _read_swc(swc_file)
    forest = _forest_complete(swc)
    stretch_type(forest)
    return forest

################################################################

####################### SWC__CSV_SWC ###########################

@ele_mani
def _tree_csv(tree, spamwriter):
    spamwriter.writerow([tree.id, tree.type, tree.r, tree.der, tree.branch_node_num, tree.dist_to_root, tree.dist_to_leaf])
    _tree_csv(tree.children, spamwriter)


def _forest_csv(forest, filename):
    with open(filename, 'wb') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter = ',', quotechar = '|', quoting = csv.QUOTE_MINIMAL)
        spamwriter.writerow(['Id', 'Type', 'Raius', 'Sec-order Der',  '#branch_points', 'Dist_to_root', 'Dist_to_leaf'])
        _tree_csv(forest, spamwriter)


@ele_mani
def _tree_swc(tree, swcfile):
    for node in tree.all_nodes:
        swcfile.write('{id}, {type}, {x}, {y}, {z}, {r}, {pid}\n'.format(
                        id = node.id, type = node.type, x = node.x, y = node.y, 
                        z = node.z, r = node.r, pid = node.pid))


def _forest_swc(forest, filename):
    with open(filename, 'wb') as swcfile:
        swcfile.write('# Id, Type, x, y, z, Radius, Parent\n')
        _tree_swc(forest, swcfile)


def swc__csv_swc(input_swc, **output):
    forest = swc_forest(input_swc)
    if 'csv' in output:
        _forest_csv(forest, output['csv'])
    if 'swc' in output:
        _forest_swc(forest, output['swc'])

################################################################

###################### SWC_PLOTS ###############################

def swc_plots(input_swc, plot_dir = PLOT_DIR):
    forest = swc_forest(input_swc)
    plot_tree(forest, plot_dir)
    

if __name__ == '__main__':
    swc_plots('../test/01.10.17_SWC-e1/01.10.17_SWC-e1.swc', '../Figs/Figs(UniSpl-extend_two_nodes)')

