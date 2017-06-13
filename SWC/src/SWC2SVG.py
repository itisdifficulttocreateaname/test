#!/usr/bin/env python
#coding: utf-8

import math
import numpy as np 
import svgwrite
import warnings

from Get_SWC_Info import swc_forest
from ele_manipulation import ele_mani


X_SCALE = 0
Y_UNIT = 15
CIRCLE_RADII = 2
TEXT_X = 3
TEXT_Y = 3
FONT_SIZE = 8
STROKE_WIDTH = 2
STROKE_1 = 'gainsboro'
STROKE_2 = 'darkgrey'
SOMA_COLOR = 'limegreen'
STROKE_VERTICAL = 'black'


########################## MERGE_SOMA ##########################

@ele_mani
def _merge(childsoma, soma):
    if childsoma.sd_type != 1:
        pass
    else:
        for child in childsoma.children:
            child.parent = soma

        childsoma.parent = None


@ele_mani
def _merge_soma(tree):
    
    if tree.sd_type != 1:        
        pass
    else:
        _merge_soma(tree.children)
        _merge(tree.children, tree)

################################################################


######################### DECORATE_NODE ########################

def _read_file(filename):   
    with open(filename, 'r') as f:
        return (line for line in f.readlines())

def _split_line(line):    
    return line.split()

### IS_VALID_DECORATOR_LINE ####

def _is_valid_len(len):    
    if not len == 6:
        raise Exception('Each line includes six elements!')

def _is_valid_pos(pos):    
    if not 0 <= pos and pos <= 1:
        raise Exception('Pos should fall in [0, 1]!')

def _is_valid_rgba(rgba):    
    for rgb in rgba[:3]:
        if not (0 <= rgb and rgb <= 255):
            raise Exception('Wrong rgb value! (integers between 0 and 255 are expected)')
    if not (0 <= rgba[3] and rgba[3] <= 1):
        raise Exception('Wrong alpha value! (float between 0 and 1 is expected)')
    
def _is_valid_decorator(line):    
    _is_valid_len(len(line))  
    _is_valid_pos(float(line[1]))  
    _is_valid_rgba(map(lambda x: float(x), line[2:6]))

################################

def get_decorator(decorator_file):
    
    lines = _read_file(decorator_file)
    decorator = {}    
    
    for line in lines:
        line = _split_line(line)
        _is_valid_decorator(line)

        decorator[line[0]] = [float(line[1]),] + map(lambda x: int(x), line[2:5]) + [float(line[5]),]
    
    return decorator


def _linear_interpolate(node, pos):
    node.xs_pos = node.xs*(1-pos) + node.parent.xs*pos if not node.is_root else node.xs
    node.ys_pos = node.ys*(1-pos) + node.parent.ys*pos if not node.is_root else node.ys    


def decorate_nodes(tree, decorator_file):

    decorator = get_decorator(decorator_file)
    
    for node in tree.all_nodes:
        
        if node.id in decorator:
            
            pos = decorator[node.id][0]
            node.rgb = svgwrite.rgb(*decorator[node.id][1:4])
            node.alpha = decorator[node.id][4]
            
            _linear_interpolate(node, pos)
            decorator.pop(node.id)
        
        else:
            node.alpha = 0
            node.rgb = svgwrite.rgb(0,0,0)
            node.xs_pos, node.ys_pos = 0, 0

    if decorator:
        warnings.warn('Decorator file has unused nodes!')

################################################################


########################## Tree2SVG ############################

def _next_BP(tree):    
    while len(tree.children) == 1:
          tree = tree.children[0]  
    return tree #real BP or leaf


def svg_circle(dwg, node, radii = CIRCLE_RADII):
    dwg.add(dwg.circle((node.xs_pos, node.ys_pos), radii,
                        stroke = node.rgb,
                        fill = node.rgb,
                        stroke_opacity = node.alpha,
                        fill_opacity = node.alpha))

def svg_node_text(dwg, node, text_x = TEXT_X, text_y = TEXT_Y, font_size = FONT_SIZE):
    dwg.add(dwg.text('%.2f'%node.dist_to_root,
                     insert = (node.xs + text_x, node.ys + text_y),
                     font_size = font_size))

def svg_leaf(dwg, tree, decorator_file = None):    
    if decorator_file:
        svg_circle(dwg, tree)

    svg_node_text(dwg, tree)

def svg_node_line(dwg, node1, node2, stroke = STROKE_1, stroke_width = STROKE_WIDTH):
    dwg.add(dwg.line((node1.xs, node1.ys), (node2.xs, node2.ys), 
                     stroke = stroke, stroke_width = stroke_width))


def tree_svg(dwg, tree, decorator_file = None, color = STROKE_1, soma_color = SOMA_COLOR):

    if tree.is_leaf:
        svg_leaf(dwg, tree, decorator_file)
    
    elif len(tree.children) == 1:        
        nextBP = _next_BP(tree)
        svg_node_line(dwg, tree, nextBP, stroke = color if tree.sd_type != 1 else soma_color)

        tree_svg(dwg, nextBP, decorator_file, color)
        
        if decorator_file:
            node = nextBP
            while node != tree:
                node = node.parent
                svg_circle(dwg, node)

    else: #BP
        dwg.add(dwg.line((tree.xs, tree.children[0].ys),
                         (tree.xs, tree.children[-1].ys),
                         stroke = STROKE_VERTICAL if tree.sd_type != 1 else soma_color,
                         stroke_width = .5))
        
        for child in tree.children:
            dwg.add(dwg.line((tree.xs, child.ys),
                             (child.xs, child.ys),
                             stroke = STROKE_2 if tree.n_BP_before == 0 and tree.children.index(child)%2 == 0 else color,
                             stroke_width = STROKE_WIDTH))
            
            tree_svg(dwg, child, decorator_file, STROKE_2 if tree.n_BP_before == 0 and tree.children.index(child)%2 == 0 else color)
        
        if decorator_file:
            svg_circle(dwg, tree)

        svg_node_text(dwg, tree, 3, 0, 6)

################################################################

########################### SWC_SVG ############################

@ele_mani
def _n_BP(tree):
    if tree.is_root:
        tree.n_BP_before = 0    
    else:
        tree.n_BP_before = tree.parent.n_BP_before if len(tree.siblings) == 0 else tree.parent.n_BP_before + 1
    
    _n_BP(tree.children)


def _leaf_id_XSCALE(tree):
    global X_SCALE
    for index, leaf in enumerate(tree.all_leaves):
        leaf.lId = index
        X_SCALE = max(X_SCALE, leaf.dist_to_root)


def _coordinate(tree):    
    global Y_UNIT

    for child in tree.children:
        _coordinate(child)    
    else:
        tree.xs = tree.dist_to_root * (1000./X_SCALE)
        tree.ys = Y_UNIT * tree.lId if tree.is_leaf else 0.5*(max(child.ys for child in tree.children)+
                                                            min(child.ys for child in tree.children))


@ele_mani
def plot_svg(tree, SVGFile, node_decorator = None):
    
    global Y_UNIT
        
    _leaf_id_XSCALE(tree)
    n_leaf = len(tree.all_leaves)
    yscale = n_leaf * Y_UNIT

    _coordinate(tree)
    dwg = svgwrite.Drawing(SVGFile, viewBox = "-100 0 1200 {yscale}".format(yscale = yscale), 
                                    preserveAspectRatio = 'center middle slice')
    
    if node_decorator:
        decorate_nodes(tree, node_decorator)
    
    tree_svg(dwg, tree, node_decorator)
    dwg.save()



def swc_svg(swcfile, svgfile, node_decorator = None, merge_soma = False):
    
    forest = swc_forest(swcfile)
    
    if merge_soma:
        _merge_soma(forest)
    
    _n_BP(forest)
    plot_svg(forest, svgfile, node_decorator)

################################################################

