#!usr/bin/env python
#encoding: utf-8

import matplotlib.colors as colors
import matplotlib.cm as cm
import matplotlib.pyplot as plt 

from Get_SWC_Info import SWC2Forest
from TreeNodes import AllTreeNodes

class Decorator(object):

    def __init__(self, tree_root, decorator_file, pos = 1.0, colormap = 'plasma'):
        super(Decorator, self).__init__()
        self.tree = tree_root
        self.pos = float(pos)
        self.decorator_file = decorator_file
        self.colormap = colormap
        self.fp = None
        self.array = [0, 255]


    def before_generation(self):
        
        if not (0 <= self.pos and self.pos <= 1):
            Exception('''"pos" should fall in interval [0, 1]!''')


    def _get_color(self, node):
        
        m = plt.get_cmap(self.colormap)
        scalarMap = cm.ScalarMappable(cmap = m)
        scalarMap.set_array(self.array)
        scalarMap.autoscale()
        return scalarMap.to_rgba(node.type, bytes = True)


    def get_color(self, node):

        r, g, b, a = self._get_color(node) # a:[0,255]
        a = 1.0*(self.array[1] - node.type)/(self.array[1] - self.array[0]) if node.is_swollen else 0
        return r, g, b, a


    def generate_decorator(self, node):
        
        if node.is_swollen:
            r, g, b, a = self.get_color(node)
            self.fp.write('{id} {pos} {r} {g} {b} {a}\n'.format(id = node.id, pos = self.pos,
                                                                r = r, g = g, b = b, a = a)) 
        for child in node.children:
            self.generate_decorator(child)


    def swell_filter(self):

        all_nodes = AllTreeNodes(self.tree)
        der_types = [node.type for node in all_nodes if node.is_swollen]
        self.array = [min(der_types), max(der_types)]


    def write_to_file(self):
        self.before_generation()
        with open(self.decorator_file, 'w') as self.fp:
            self.swell_filter()
            self.generate_decorator(self.tree)


def swc_decorator(swcfile, pos = 1.0, colormap = 'plasma'):
    forest = SWC2Forest(swcfile)
    for tree in forest:
        decorator = Decorator(tree, '../decorator%s.txt'%forest.index(tree))
        decorator.write_to_file()


if __name__ == '__main__':
    swc_decorator('../test.swc')
