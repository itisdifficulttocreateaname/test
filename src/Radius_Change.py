#!/usr/bin/env python
#coding: utf-8

import os
import math
import matplotlib.pyplot as plt 
from scipy import interpolate
import numpy as np
from copy import deepcopy

from ele_manipulation import ele_mani
from globals import my_global

my_global = my_global()
R_RESCALE = my_global.r_rescale 
#R_RESCALE = 1.0
R_STRETCH = 2
SYM_EXT_N = 2
SPL_ORDER = 4
DER_ORDER = 2
PLOT_DIR = './Figs/Figs(UniSpl-extend_two_nodes)'


def _leaf_XY(leaf, X, Y):

    node = leaf 
    while True:
        X.insert(0, node.dist_to_root)
        Y.insert(0, node.r)
        if node.is_root:
            break
        node = node.parent


def _sym_extend(X, Y, n = SYM_EXT_N):
    if len(X) >= SYM_EXT_N+1:
        X_ext, Y_ext = deepcopy(X), deepcopy(Y)
        X_ext = X_ext + map(lambda x: 2*X_ext[-1]-x, X_ext[-2:-2-n:-1])
        Y_ext = Y_ext + Y_ext[-2:-2-n:-1]
        return X_ext, Y_ext
    elif len(X) == SYM_EXT_N:
        n = SYM_EXT_N-1
        X_ext, Y_ext = deepcopy(X), deepcopy(Y)
        X_ext = X_ext + X_ext[-2:-2-n:-1]
        Y_ext = Y_ext + Y_ext[-2:-2-n:-1]
        return X_ext, Y_ext
    else:
        pass


def _LinearInterpolation(x, y):

    f = interpolate.interp1d(x, y, kind = 'slinear')
    delta_y = np.median(tuple(abs(y[i]-y[i-1]) for i in range(1, len(x))))
    xnew = deepcopy(x)
    while len(x) <= 4:
        xnew += [0]*(len(xnew)-1)
        for i in range(1, len(x)):
            xnew[2*i] = x[i]
            xnew[2*i-1] = .5*(x[i]+x[i-1])
        x = deepcopy(xnew)
    y = map(f, x)
    delta_y = np.median(tuple(abs(y[i]-y[i-1]) for i in range(1, len(x))))

    for i in range(len(x)-2, -1, -1):
        
        if abs(y[i+1]-y[i]) > delta_y and delta_y != 0:
            n = int(abs(y[i+1]-y[i]) / delta_y)
            n = min(n, 100)
            for j in range(n, 0, -1):
                xnew.insert(i+1, x[i] + (x[i+1]-x[i])*j/(n+1))
        
        elif x[i+1]-x[i] > (max(x)-min(x))/(len(x)-1):
            n = int((x[i+1]-x[i])/(max(x)-min(x))*len(x))
            for j in range(n, 0, -1):
                xnew.insert(i+1, x[i] + (x[i+1]-x[i])*j/(n+1))

    ynew = map(f, xnew)
    return xnew, ynew


@ele_mani
def _generate_der(leaf, extent_n = SYM_EXT_N):
    X, Y = [], [] 
    _leaf_XY(leaf, X, Y)

    X_ext, Y_ext = _sym_extend(X, Y, extent_n) if len(X) > 2 else (X, Y) 
    Xnew, Ynew = _LinearInterpolation(X_ext[2:], Y_ext[2:]) if len(X_ext) > 3 else _LinearInterpolation(X_ext, Y_ext)
    Xnew, Ynew = _LinearInterpolation(Xnew, Ynew)

    f = interpolate.UnivariateSpline(Xnew, Ynew, k = SPL_ORDER)      
    
    for index, node in enumerate(leaf.path):
        der = f.derivative(n = DER_ORDER)(X[index]) if index != 0 else 0
        node.der = filter(lambda x: abs(x) <= abs(der), (node.der, der))[0] if node.der else der

    return f, X, Y

####################### MARK_ALL_DERS ##########################

def mark_all_ders(tree, extent_n = SYM_EXT_N):
    tree.tree_para_rescale(r = 1. / R_RESCALE * R_STRETCH)

    _generate_der(tree.all_leaves, extent_n)

    tree.tree_para_rescale(r = 1. * R_RESCALE / R_STRETCH)

################################################################

####################### PLOT_TREE ##############################

def _Draw(f, x, y):

    xnew = np.arange(min(x[2:]), max(x[2:]), (max(x[2:])-min(x[2:]))/(len(x)*50))
    ynew = map(f, xnew)
    
    der = map(f.derivative(n = DER_ORDER), x[2:])
    dernew = map(f.derivative(n = DER_ORDER), xnew)
    
    fig, left_axis = plt.subplots()
    right_axis = left_axis.twinx()

    p1, = left_axis.plot(xnew, ynew, 'b-')
    p1, = left_axis.plot(x, y, 'bo')  
    p2, = right_axis.plot(xnew, dernew, 'r:')
    p2, = right_axis.plot(x[2:], der, 'r.')

    left_axis.set_xlabel('Distance to root')
    left_axis.set_ylabel('Radius')
    right_axis.set_ylabel('Second-order derivative')


@ele_mani
def _radii_plot(leaf, plot_dir = PLOT_DIR):

    f, X, Y = _generate_der(leaf)
    _Draw(f, X, Y) 

    plt.savefig(plot_dir + '/leaf{id}.png'.format(id = leaf.id))
    plt.clf()
    plt.close('all')


@ele_mani
def plot_tree(tree, plot_dir = PLOT_DIR):
    tree.tree_para_rescale(r = 1. / R_RESCALE * R_STRETCH)

    _radii_plot(tree.all_leaves, plot_dir)

    tree.tree_para_rescale(r = 1. * R_RESCALE / R_STRETCH)
   
################################################################
