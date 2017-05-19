#!/usr/bin/env python
#coding: utf-8

import os
import argparse

from SWC2SVG import swc_svg


def get_output(output, default_name):
    output_file = output    
    if not output_file.endswith('.svg'):
        if not os.path.isdir(output_file):
            os.makedirs(output_file)
        output_file = os.path.join(output_file, os.path.split(default_name)[1][:-4]+'.svg')
    else:
        if not os.path.isdir(os.path.split(output_file)[0]):
            os.makedirs(os.path.split(output_file)[0])
    
    return output_file


def process_cmd(input_file, output):
    if not os.path.isfile(input_file):
        IOError('{0} does not exists!'.format(input_file))
        
    output_file = get_output(output, input_file)
    return input_file, output_file


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file')
    parser.add_argument('-o', action = 'store', default = r'./',
                        help = 'output filename or directory')
    parser.add_argument('--node', action = 'store', default = None, 
                        help = 'node decorator')
    parser.add_argument('--merge_soma', action = 'store_true',
                        help = 'merge all soma nodes')
    args = parser.parse_args()

    swcfile, svgfile = process_cmd(args.input_file, args.o)
    swc_svg(swcfile, svgfile, args.node, args.merge_soma)
    print('Successfully created svg file: %s'%svgfile)
