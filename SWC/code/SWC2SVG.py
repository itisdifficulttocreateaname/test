#!/usr/bin/env python
#coding: utf-8

import math
import numpy as np 
import svgwrite
import matplotlib.colors as colors
import matplotlib.cm as cm
import matplotlib.pyplot as plt

from Get_SWC_Info import readSWCFile, completeForest
from StretchType import Stretch_Type

from Get_SWC_Info import SWC2Forest


def GetColor(ntype):
    m = plt.get_cmap('plasma')
    scalarMap = cm.ScalarMappable(cmap = m)
    scalarMap.set_array([0,255])
    scalarMap.autoscale()
    #print scalarMap.to_rgba(ntype)
    return scalarMap.to_rgba(ntype, bytes = True)


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



def Tree2SVG(dwg, tree, color = 'royalblue'):

    if tree.is_leaf:
        dwg.add(dwg.circle((tree.xs, tree.ys), 2, 
                            stroke = svgwrite.rgb(*GetColor(tree.type)[:3]),
                            #stroke = svgwrite.rgb(GetColor(tree.type)[0]*100, GetColor(tree.type)[1]*100, GetColor(tree.type)[2]*100, '%'),  
                            stroke_opacity = GetColor(tree.type)[3],
                            fill = svgwrite.rgb(*GetColor(tree.type)[:3])))
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
        Tree2SVG(dwg, nextBP, color)
        node = nextBP
        while node != tree:
            node = node.parent
            dwg.add(dwg.circle((node.xs, node.ys), 2, 
                                stroke = svgwrite.rgb(*GetColor(node.type)[:3]),
                                #stroke = svgwrite.rgb(GetColor(node.type)[0]*100, GetColor(node.type)[1]*100, GetColor(node.type)[2]*100, '%'),  
                                stroke_opacity = GetColor(node.type)[3],
                                fill = svgwrite.rgb(*GetColor(node.type)[:3])))


    else:
        dwg.add(dwg.line((tree.xs, tree.children[0].ys),
                         (tree.xs, tree.children[-1].ys),
                         stroke = 'black' if tree.sd_type != 1 else 'limegreen',
                         stroke_width = .5))
        
        for child in tree.children:            
            dwg.add(dwg.line((tree.xs, child.ys),
                             (child.xs, child.ys),
                             stroke = 'pink' if tree.N_BP == 0 and tree.children.index(child)%2 == 0 else color,
                             stroke_width = 2))
            
            Tree2SVG(dwg, child, 'pink' if tree.N_BP == 0 and tree.children.index(child)%2 == 0 else color)
        
        dwg.add(dwg.circle((tree.xs, tree.ys), 2,
                            stroke = svgwrite.rgb(*GetColor(tree.type)[:3]),
                            #stroke = svgwrite.rgb(GetColor(tree.type)[0]*100, GetColor(tree.type)[1]*100, GetColor(tree.type)[2]*100, '%'), 
                            stroke_opacity = GetColor(tree.type)[3],
                            fill = svgwrite.rgb(*GetColor(tree.type)[:3])))

        dwg.add(dwg.text('%.2f'%tree.dist_to_root,
                 insert = (tree.xs + 3, tree.ys ),
                 font_size = '6'))                



def DrawSVG(forest, SVGFile):
    global n_leaf, yunit

    for tree in forest:
        _n_leaf(tree)
        _CalCoor(tree)
        dwg = svgwrite.Drawing(SVGFile, viewBox = "-100 0 1200 %s"%(n_leaf*yunit))
        Tree2SVG(dwg, tree)
        dwg.save()


def merge(soma, childsoma):
    soma.children += childsoma.children
    soma.children.remove(childsoma)

def merge_soma(tree):
    if tree.sd_type != 1:
        pass
    else:
        for child in tree.children:
            if child.sd_type == 1:
                merge_soma(child)
                merge(tree, child)


def MergeSoma(forest):
    map(merge_soma, forest)


if __name__ == '__main__':
    import os
    abs_path = os.path.dirname(os.path.abspath(__file__))
    testfile_path = os.path.join(abs_path, '..','test.swc')
    result_path = os.path.join(abs_path, '..', 'neuron.svg')
    forest = SWC2Forest(testfile_path)
    Process(forest)
    MergeSoma(forest)
    DrawSVG(forest, result_path)

