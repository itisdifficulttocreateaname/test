#!/usr/bin/env python
#coding: utf-8

import os
import argparse

from SWC2SVG import swc_svg
from cmd import filepath, check_args


@check_args
def _process_cmd(args):
    output_file = filepath(args.o, args.input_file, format = 'svg')
    
    return args.input_file, output_file

def _args_to_check(args):
    vars(args)['check'] = {}
    args.check['input_swc'] = [args.input_file, 'swc']
    if args.node:
        args.check['node_decorator'] = [args.node, 'txt']

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('input_file')
    parser.add_argument('-o', action = 'store', default = r'./',
                        help = 'output filename or directory')
    parser.add_argument('--node', action = 'store', default = None, 
                        help = 'node decorator')
    parser.add_argument('--merge_soma', action = 'store_true',
                        help = 'merge all soma nodes')
    args = parser.parse_args()
    _args_to_check(args)

    swcfile, svgfile = _process_cmd(args)
    swc_svg(swcfile, svgfile, args.node, args.merge_soma)
    print('Successfully created svg file: {svgfile}'.format(svgfile = svgfile))



if __name__ == '__main__':
    
    main()