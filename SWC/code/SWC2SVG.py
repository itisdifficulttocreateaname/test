#!/usr/bin/env python
#coding: utf-8

import math
import numpy as np 
import svgwrite

from StretchType import Stretch_Type
from Get_SWC_Info import SWC2Forest
from TreeNodes import AllTreeNodes


def process(tree):

    if tree.is_root:
        tree.N_BP = 0    
    else:
        tree.N_BP = tree.parent.N_BP if len(tree.siblings) == 0 else tree.parent.N_BP + 1
    
    for child in tree.children:
        process(child)



def Process(forest):
    map(process, forest)



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



def read_file(filename):
    
    with open(filename, 'r') as f:
        return (line for line in f.readlines())



def split_line(line):
    
    return line.split()



def is_valid_len(len):
    
    return len == 6

def is_valid_pos(pos):
    
    return 0 <= pos and pos <= 1

def is_valid_rgba(*args):
    
    for arg in args[:3]:
        if not (0 <= arg and arg <= 255):
            return False
    if not (0 <= args[3] and args[3] <= 1):
        return False
    
    return True 

def is_valid_decorator(line):
    
    return is_valid_len(len(line)) and is_valid_pos(float(line[1])) and is_valid_rgba(lambda x: float(x), line[2:6])



def get_decorator(node_decorator_file):
    
    lines = read_file(node_decorator_file)
    decorator = {}    
    
    for line in lines:
        line = split_line(line)
        if not is_valid_decorator(line):
            Exception('Invalid decorator text!')
        decorator[line[0]] = [float(line[1]),] + map(lambda x: int(x), line[2:5]) + [float(line[5]),]
    
    return decorator



def decorate_node(tree, node_decorator):
    
    decorator = get_decorator(node_decorator)
    all_nodes = AllTreeNodes(tree)
    
    for node in all_nodes:
        if node.id in decorator:
            pos = decorator[node.id][0]
            node.rgb = svgwrite.rgb(*decorator[node.id][1:4])
            node.alpha = decorator[node.id][4]
            node.xs_pos = node.xs*pos + node.parent.xs*(1-pos) if not node.is_root else node.xs
            node.ys_pos = node.ys*pos + node.parent.ys*(1-pos) if not node.is_root else node.ys
            decorator.pop(node.id)
        else:
            node.alpha = 0
            node.rgb = svgwrite.rgb(0,0,0)
            node.xs_pos, node.ys_pos = 0, 0

    if decorator:
        UserWarning('Decorator file has unused nodes!')



def Tree2SVG(dwg, tree, node_decorator = None, color = 'lightblue'):

    if tree.is_leaf:
        
        if node_decorator != None:
            dwg.add(dwg.circle((tree.xs_pos, tree.ys_pos), 2,
                                stroke = tree.rgb,
                                fill = tree.rgb,
                                stroke_opacity = tree.alpha,
                                fill_opacity = tree.alpha))
        
        dwg.add(dwg.text('%.2f'%tree.dist_to_root,
                         insert = (tree.xs + 3, tree.ys + 3),
                         font_size = '8'))                

    elif len(tree.children) == 1:
        
        global _n_BP 
        _n_BP = 0
        nextBP = NextBP(dwg, tree)
        dwg.add(dwg.line((tree.xs, tree.ys), 
                         (nextBP.xs, nextBP.ys), 
                         stroke = color if tree.sd_type != 1 else 'limegreen',
                         stroke_width = 2))
        
        Tree2SVG(dwg, nextBP, node_decorator, color)
        
        node = nextBP
        while node != tree:
            node = node.parent
            if node_decorator != None:
                dwg.add(dwg.circle((node.xs_pos, node.ys_pos), 2,
                                    stroke = node.rgb,
                                    fill = node.rgb,
                                    stroke_opacity = node.alpha,
                                    fill_opacity = node.alpha))

    else:

        dwg.add(dwg.line((tree.xs, tree.children[0].ys),
                         (tree.xs, tree.children[-1].ys),
                         stroke = 'black' if tree.sd_type != 1 else 'limegreen',
                         stroke_width = .5))
        
        for child in tree.children:            
            dwg.add(dwg.line((tree.xs, child.ys),
                             (child.xs, child.ys),
                             stroke = 'darkgrey' if tree.N_BP == 0 and tree.children.index(child)%2 == 0 else color,
                             stroke_width = 2))
            
            Tree2SVG(dwg, child, node_decorator, 'darkgrey' if tree.N_BP == 0 and tree.children.index(child)%2 == 0 else color)
        
        if node_decorator != None:
            dwg.add(dwg.circle((tree.xs_pos, tree.ys_pos), 2,
                                stroke = tree.rgb,
                                fill = tree.rgb,
                                stroke_opacity = tree.alpha,
                                fill_opacity = tree.alpha))

        dwg.add(dwg.text('%.2f'%tree.dist_to_root,
                 insert = (tree.xs + 3, tree.ys ),
                 font_size = '6'))                



def DrawSVG(forest, SVGFile, node_decorator = None):
    
    global n_leaf, yunit

    for tree in forest:
        
        _n_leaf(tree)
        _CalCoor(tree)
        dwg = svgwrite.Drawing(SVGFile, viewBox = "-100 0 1200 %s"%(n_leaf*yunit), preserveAspectRatio = 'center middle slice')
        
        if node_decorator != None: 
            decorate_node(tree, node_decorator)
        
        Tree2SVG(dwg, tree, node_decorator)
        dwg.save()



def merge(soma, childsoma):
    
    for child in childsoma.children:
        child.parent = soma
    
    childsoma.parent = None



def merge_soma(tree):
    
    if tree.sd_type != 1:        
        pass
    else:
        for child in tree.children:
            if child.sd_type == 1:
                merge_soma(child)
                merge(tree, child)



def MergeSoma(forest):
    
    for tree in forest:        
        if tree.sd_type != 1:
            UserWarning('Root node is not a soma!')
        else: 
            merge_soma(tree)



def swc_svg(swcfile, svgfile, node_decorator = None, merge_soma = False):
    
    forest = SWC2Forest(swcfile)
    
    if merge_soma:
        MergeSoma(forest)
    
    Process(forest)
    DrawSVG(forest, svgfile, node_decorator)


