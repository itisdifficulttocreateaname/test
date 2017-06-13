#!usr/bin/env python
#encoding: utf-8

import sys
import os
import argparse
import numpy as np 

from Get_SWC_Info import swc_forest
from cmd import filepath, check_args


class Decorator(object):

    def __init__(self, tree_root, decorator_file, colormap_file, pos = 0.0):
        super(Decorator, self).__init__()
        self.tree = tree_root
        self._pos = None
        self.pos = float(pos)
        self.decorator_file = decorator_file
        self.colormap = colormap_file
        self.decorator_fp = None
        self.colormap_fp = None

    @property
    def pos(self):
        return self._pos

    @pos.setter
    def pos(self, new_value):
        if new_value < 0 or new_value > 1:
            raise Exception("'pos' should fall in interval [0, 1]!")
        else:
            self._pos = new_value

    def parse_colormap_file(self):
        colormap = {}
        with open(self.colormap, 'r') as self.colormap_fp:
            for line in self.colormap_fp.readlines():
                line = line.split()
                colormap[int(line[0])] = map(lambda x: int(x), line[1:5])

        return colormap


    def nearest_nums(self, num, list):
        m, M = None, None
        
        for item in list:
            if item < num:
                m = item if not m else max(item, m)
            else:
                M = item if not M else min(item, M)

        return m, M


    def _get_color(self, node):
        colormap = self.parse_colormap_file()
        min_color_index = min(colormap.keys())
        max_color_index = max(colormap.keys())

        if node.type < min_color_index:
            return colormap[min_color_index]
        elif node.type > max_color_index:
            return colormap[max_color_index]
        else:
            if colormap.has_key(node.type):
                return colormap[node.type]
            else:
                m, M = self.nearest_nums(node.type, colormap.keys())
                Lambda = 1. * (node.type-m) / (M-m)
                rgba = Lambda * np.array(colormap[m]) + (1-Lambda) * np.array(colormap[M])
                return list(map(lambda x: int(round(x)), rgba))


    def get_color(self, node):

        r, g, b, a = self._get_color(node) # a:[0,255]
        a /= 255.
        return r, g, b, a


    def generate_decorator(self, node):
        
        if node.is_der_loc_min and node.is_swollen:
            r, g, b, a = self.get_color(node)
            self.decorator_fp.write('{id} {pos} {r} {g} {b} {a}\n'.format(id = node.id, pos = self.pos,
                                                                r = r, g = g, b = b, a = a)) 
        
        map(self.generate_decorator, node.children)


    def write_to_file(self):       
        with open(self.decorator_file, 'wb') as self.decorator_fp:
            self.generate_decorator(self.tree)



def swc_decorator(swcfile, decorator_file, colormap_file, pos = 0.0):
    
    forest = swc_forest(swcfile)
    for tree in forest:
        decorator = Decorator(tree, decorator_file, colormap_file)
        decorator.write_to_file()


@check_args
def _process_cmd(args):    
    output_file = filepath(args.o, args.input_file, format = 'txt', suffix = 'decorator')

    return args.input_file, output_file, args.color_map

def _args_to_check(args):
    vars(args)['check'] = {}
    args.check['input_swc'] = [args.input_file, 'swc']
    args.check['color_map'] = [args.color_map, 'txt']


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file', help = 'swc format file')
    parser.add_argument('-o', action = 'store', default = r'./',
                        help = 'output filename or directory')
    parser.add_argument('--color_map', action = 'store', default = None,
                        help = 'txt format colormap file')
    args = parser.parse_args()
    _args_to_check(args)

    swc_file, decorator_file, colormap_file = _process_cmd(args)
    swc_decorator(swc_file, decorator_file, colormap_file)
    
    print('Successfully created %s!'%decorator_file)



if __name__ == '__main__':

    main()