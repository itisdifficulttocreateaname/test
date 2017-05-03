#!/usr/bin/env python
#coding: utf-8

import math
import numpy as np 
import svgwrite
from anytree import Node


class NeuronNode(Node):
    def __init__(self, id, type, x, y, z, r, pid):
        super(Node, self).__init__()
        self.name = id
        self.id = id
        self.type = int(type)
        self.x = float(x) * 0.0884
        self.y = float(y) * 0.0884
        self.z = float(z) 
        self.r = float(r) * 0.0884
        self.pid = pid

        self.parent = None
        self.dist_to_root = 0
        self.N_BP = 0
        self.xs = 0
        self.ys = 0


def readSWCFile(filename):
    with open(filename, 'r') as f:
        return (line for line in f.readlines() if not line.startswith('#'))


def d(n1, n2):
    return math.sqrt((n1.x - n2.x)**2 + (n1.y - n2.y)**2 + (n1.z - n2.z)**2)


def parseLine(line):
    return NeuronNode(*line.split())


def process(tree):
    if tree.is_root:
        pass
    else:
        tree.dist_to_root = tree.parent.dist_to_root + d(tree, tree.parent)
        tree.N_BP = tree.parent.N_BP if len(tree.siblings) == 0 else tree.parent.N_BP + 1
    
    for child in tree.children:
        process(child)
    

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
                
    return forest


##############################################################


def SWC2Forest(filename):
    swc = readSWCFile(filename)
    return createForest(swc)


xscale = 0
n_leaf = 0

def _n_leaf(tree):
    global n_leaf, xscale

    if tree.is_leaf:
        n_leaf += 1
        tree.lId = n_leaf
        if tree.dist_to_root > xscale:
            xscale = tree.dist_to_root
    else:
        for child in tree.children:
            _n_leaf(child)


yunit = 15

def _CalCoor(tree):
    global yunit

    for child in tree.children:
        _CalCoor(child)
    
    else:
        tree.xs = tree.dist_to_root * (1000./xscale)
        tree.ys = yunit * tree.lId if tree.is_leaf else .5*(max(child.ys for child in tree.children)+
                                                            min(child.ys for child in tree.children))


_n_BP = 0
def NextBP(dwg, tree):
    global _n_BP     
    
    if len(tree.children) == 1:
        _n_BP += 1
        return NextBP(dwg, tree.children[0])
    else:
        return tree


def Tree2SVG(dwg, tree, color = 'royalblue'):

    if tree.is_leaf:
        dwg.add(dwg.circle((tree.xs, tree.ys), 2)) 

    elif len(tree.children) == 1:
        global _n_BP 
        _n_BP = 0
        nextBP = NextBP(dwg, tree)
        dwg.add(dwg.line((tree.xs, tree.ys), 
                         (nextBP.xs, nextBP.ys), 
                         stroke = color if tree.type != 1 else 'limegreen',
                         stroke_width = 2))
        dwg.add(dwg.text('%s'%_n_BP, 
                         insert = (nextBP.xs + 3, nextBP.ys + 3),
                         font_size = '11'))
        Tree2SVG(dwg, nextBP, color)
        node = nextBP
        while node != tree:
            node = node.parent
            dwg.add(dwg.circle((node.xs, node.ys), 2)) 

    else:
        dwg.add(dwg.line((tree.xs, tree.children[0].ys),
                         (tree.xs, tree.children[-1].ys),
                         stroke = 'black' if tree.type != 1 else 'limegreen',
                         stroke_width = .5))
        for child in tree.children:
            dwg.add(dwg.line((tree.xs, child.ys),
                             (child.xs, child.ys),
                             stroke = 'pink' if tree.N_BP == 0 and tree.children.index(child)%2 == 0 else color,
                             stroke_width = 2))
            if len(child.children) != 1: 
                dwg.add(dwg.text('0',
                                 insert = (child.xs + 3, child.ys + 3),
                                 font_size = '11'))                
            Tree2SVG(dwg, child, 'pink' if tree.N_BP == 0 and tree.children.index(child)%2 == 0 else color)
        else:
            dwg.add(dwg.circle((tree.xs, tree.ys), 2)) 


def DrawSVG(forest, SVGFile):
    global n_leaf, yunit

    for tree in forest:
        _n_leaf(tree)
        _CalCoor(tree)
        dwg = svgwrite.Drawing(SVGFile, viewBox = "-100 0 1200 %s"%(n_leaf*yunit))
        Tree2SVG(dwg, tree)
        dwg.save()


if __name__ == '__main__':
    forest = SWC2Forest('test.swc')
    DrawSVG(forest, 'neuron.svg')

