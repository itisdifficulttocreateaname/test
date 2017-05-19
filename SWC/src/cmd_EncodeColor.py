#!usr/bin/env python
#encoding: utf-8

import sys
import os
import argparse
import numpy as np 

from Get_SWC_Info import SWC2Forest
from TreeNodes import AllTreeNodes


class Decorator(object):

    def __init__(self, tree_root, decorator_file, colormap_file, pos = 0.0):
        super(Decorator, self).__init__()
        self.tree = tree_root
        self.pos = float(pos)
        self.decorator_file = decorator_file
        self.colormap = colormap_file
        self.decorator_fp = None
        self.colormap_fp = None


    def before_generation(self):
        
        if not (0 <= self.pos and self.pos <= 1):
            Exception('''"pos" should fall in interval [0, 1]!''')


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
                m = item if m is None else max(item, m)
            else:
                M = item if M is None else min(item, M)

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
        for child in node.children:
            self.generate_decorator(child)


    def write_to_file(self):       
        self.before_generation()        
        with open(self.decorator_file, 'wb') as self.decorator_fp:
            self.generate_decorator(self.tree)



def swc_decorator(swcfile, decorator_file, colormap_file, pos = 0.0):
    
    forest = SWC2Forest(swcfile)
    for tree in forest:
        decorator = Decorator(tree, decorator_file, colormap_file)
        decorator.write_to_file()



def get_output(output, default_name):
    
    output_file = output
    
    if not output_file.endswith('.txt'):
        if not os.path.isdir(output_file):
            os.makdirs(output_file)
        output_file = os.path.join(output_file, os.path.split(default_name)[1][:-4]+'_decorator.txt')
    
    else:
        if not os.path.isdir(os.path.split(output_file)[0]):
            os.makdirs(os.path.split(output_file)[0])

    return output_file



def process_command(args):    
    check_arguments(args)
    output_file = get_output(args.o, args.input_file)

    return args.input_file, output_file, args.color_map


def check_arguments(args):
    if args.color_map is None:
        sys.exit('Colormap is needed!')

    if not args.input_file.lower().endswith('.swc'):
        sys.exit('Wrong input format!')
    elif not os.path.isfile(args.input_file):
        sys.exit('{} does not exists!'.format(args.input_file))
    
    if not os.path.isfile(args.color_map):
        sys.exit('{} does not exists!'.format(args.color_map))



if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('input_file', help = 'swc format file')
    parser.add_argument('-o', action = 'store', default = r'./',
                        help = 'output filename or directory')
    parser.add_argument('--color_map', action = 'store', default = None,
                        help = 'txt format colormap file')
    args = parser.parse_args()

    swc_file, decorator_file, colormap_file = process_command(args)
    swc_decorator(swc_file, decorator_file, colormap_file)
    
    print('Successfully created %s!'%decorator_file)
