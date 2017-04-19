#!/usr/bin/env python
#coding: utf-8

import math
import matplotlib.pyplot as plt 
from scipy import interpolate
import numpy as np

global delta

def Get_XY(leaf, X, Y):
    node = leaf 
    while True:
        X.insert(0, node.dist_to_root)
        Y.insert(0, node.r)
        if node.is_root:
            break
        node = node.parent


def Cal_Derivative(f):
    def Df(x):
        global delta
        return (f(x+delta)-f(x-delta))/(2*delta)
    return Df 


def DrawBranch(leaf):
    x, y = [], []
    Get_XY(leaf, x, y)
    f = interpolate.UnivariateSpline(x, y)
    xnew = np.arange(min(x), max(x), (max(x)-min(x))/(len(x)*50))
    ynew = map(f, xnew)
    plt.plot(x, y, 'o', xnew, ynew, '-')
    plt.savefig('Figs/leaf%s.jpg'%leaf.id)
    plt.clf()


def Mark_Derivative(leaf):
    # X：从root到leaf的路径上所有点到root的’折线和‘距离
    # Y：从root到leaf的路径上所有点的半径
    X, Y = [], [] 
    Get_XY(leaf, X, Y)

    global delta
    delta = X[1]/10000.

    f = interpolate.UnivariateSpline(X, Y) #用三次样条插值模拟出f   
    Sec_diff = map(Cal_Derivative(Cal_Derivative(f)), X)
    
    for node in leaf.path:
        diff = Sec_diff.pop()
        if node.diff is None:
            node.diff = diff
        else:
            node.diff = min(node.diff, diff)
        



