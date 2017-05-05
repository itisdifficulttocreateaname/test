#!/usr/bin/env python
#coding: utf-8

import os
import math
import matplotlib.pyplot as plt 
from scipy import interpolate
import numpy as np
from copy import deepcopy

from TreeNodes import TreeLeaves
from TreeParaRescale import TreeParaRescale


def _Get_XY(leaf, X, Y):

    node = leaf 
    while True:
        X.insert(0, node.dist_to_root)
        Y.insert(0, node.r)
        if node.is_root:
            break
        node = node.parent


def _Draw(f, x, y):

    xnew = np.arange(min(x), max(x), (max(x)-min(x))/(len(x)*50))
    ynew = map(f, xnew)
    
    der = map(f.derivative(n = 2), x)
    dernew = map(f.derivative(n = 2), xnew)
    
    fig, left_axis = plt.subplots()
    right_axis = left_axis.twinx()

    p1, = left_axis.plot(xnew, ynew, 'b-')
    p1, = left_axis.plot(x, y, 'bo')  
    p2, = right_axis.plot(xnew, dernew, 'r:')
    p2, = right_axis.plot(x, der, 'r.')

    left_axis.set_xlabel('Distance to root')
    left_axis.set_ylabel('Radius')
    right_axis.set_ylabel('Second-order derivative')


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


def _Mark_Derivative(leaf):

    # X:'dist_to_root' of each node.
    # Y: radius 
    X, Y = [], [] 
    _Get_XY(leaf, X, Y)
    Xnew, Ynew = _LinearInterpolation(X, Y)
    Xnew, Ynew = _LinearInterpolation(Xnew, Ynew)

    f = interpolate.UnivariateSpline(Xnew, Ynew, k = 4)  
    #f = interpolate.InterpolatedUnivariateSpline(Xnew, Ynew, k = 4)    
    
    Sec_der = map(f.derivative(n = 2), X)
    
    for node in leaf.path:      
        der = Sec_der.pop(0)

        if node.is_leaf:
            node.der = 0
            node.parent.der = 0
        elif node.der is None:
            node.der = der
        else:
            node.der = filter(lambda x: abs(x)<=abs(der), (node.der, der))[0]
    return f, X, Y


def _Radii_plot(leaf):
    f, X, Y = _Mark_Derivative(leaf)
    _Draw(f, X, Y) 

    abs_path = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(abs_path, '..', 'Figs', 'Figs(UniSpl-derivative)')
    plt.savefig('%s/leaf%s.png'%(output_path, leaf.id))
    plt.clf()
    plt.close('all')


def MarkTreeDer(tree):
    TreeParaRescale(tree, **{'r': 1/0.0884*2})

    leaves = TreeLeaves(tree)
    map(_Mark_Derivative, leaves)

    TreeParaRescale(tree, **{'r': 0.5*0.0884})



def PlotTree(tree):
    TreeParaRescale(tree, **{'r': 1/0.0884*2})

    leaves = TreeLeaves(tree)
    map(_Radii_plot, leaves)

    TreeParaRescale(tree, **{'r': 0.5*0.0884})
   

def PlotForest(forest):
    for tree in forest:
        PlotTree(tree)
    