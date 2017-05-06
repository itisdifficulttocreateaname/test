#!usr/bin/env python
#encoding: utf-8

import matplotlib.colors as colors
import matplotlib.cm as cm
import matplotlib.pyplot as plt 

from Get_SWC_Info import SWC2Forest

class Decorator(object):

    def __init__(self, tree_root, pos, decorator_file, colormap = 'plasma'):
        super(Decorator, self).__init__()
        self.tree = tree_root
        self.pos = float(pos)
        self.decorator_file = decorator_file
        self.colormap = colormap
        self.fp = None


    def before_generation(self):
        
        if not (0 <= self.pos and self.pos <= 1):
            Exception('''"pos" should fall in interval [0, 1]!''')


    def get_color(self, node):
        
        m = plt.get_cmap(self.colormap)
        scalarMap = cm.ScalarMappable(cmap = m)
        scalarMap.set_array([0, 255])
        scalarMap.autoscale()
        return scalarMap.to_rgba(node.type, bytes = True)


    def generate_decorator(self, node):
        
        r, g, b, a = self.get_color(node)
        self.fp.write('{id} {pos} {r} {g} {b} {a}\n'.format(id = node.id, pos = self.pos,
                                                            r = r, g = g, b = b, a = a))
        for child in node.children:
            self.generate_decorator(child)


    def write_to_file(self):
        self.before_generation()
        with open(self.decorator_file, 'w') as self.fp:
            self.generate_decorator(self.tree)



if __name__ == '__main__':
    forest = SWC2Forest('../test.swc')
    for tree in forest:
        decorator = Decorator(tree, 1.0, '../decorator%s.txt'%forest.index(tree))
        decorator.write_to_file()
