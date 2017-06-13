#!/usr/bin/env python
#coding: utf-8

import math
from scipy.stats import mode

from Radius_Change import mark_all_ders
from ele_manipulation import ele_mani


def _Fstretch(list):
    m, M = min(list), max(list)
    lmode = 0
    scale = max(lmode - m, M - lmode)

    def fstretch(x):
        return int(255/(1+math.exp(-(12./scale)*(x-lmode)))) #logistic

    return fstretch


def _is_der_loc_min(node):
    if node.is_root: 
        return False
    if node.der > node.parent.der:
        return False
    if node.is_leaf:
        return True
    for child in node.children:
        if node.der > child.der:
            return False
    return True


@ele_mani
def stretch_type(tree):
    mark_all_ders(tree)

    all_nodes = tree.all_nodes
    all_der = [node.der for node in all_nodes]

    fstretch = _Fstretch(all_der)
    for node in all_nodes:
        node.type = fstretch(node.der)
        node.is_swollen = True if node.der <= 0 else False        
        node.is_der_loc_min = _is_der_loc_min(node)

