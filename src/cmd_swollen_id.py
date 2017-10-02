#!/usr/bin/env python
#coding: utf-8

import os
import argparse

from swollen_id import swc_swollenID_csv
from cmd import filepath, check_args

@check_args
def _process_cmd(args):

    output_csvfile = filepath(args.output_csvfile, args.input_swcfile, format = 'csv', 
                                suffix = 'swollen_'+'_'.join(str(e) for e in args.swollen_range)) 
    return args.input_swcfile, output_csvfile


def _args_to_check(args):
    vars(args)['check'] = {}
    args.check['input_swc'] = [args.input_swcfile, 'swc']


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('input_swcfile')
    parser.add_argument('-r', '--swollen_range', type = int, nargs = '*', action = 'store', default = (0, 50),
                        help = 'range to determine swollen or not')
    parser.add_argument('-c', '--output_csvfile', action = 'store', default = r'./',
                        help = 'output csv filename of directory')
    parser.add_argument('--mode', action = 'store', default = 'type', 
                        help = "data type for judging swell. Options: 'type', 'derivative'")
    args = parser.parse_args()
    _args_to_check(args)

    input_swcfile, output_csvfile = _process_cmd(args)

    swc_swollenID_csv(input_swcfile, output_csvfile, args.mode, *(args.swollen_range))
    print('Successfully created %s!\n'%(output_csvfile,))


if __name__ == '__main__':
    main()


