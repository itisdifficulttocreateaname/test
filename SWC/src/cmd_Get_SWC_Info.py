#!/usr/bin/env python
#coding: utf-8

import os
import argparse

from Get_SWC_Info import swc__csv_swc
from cmd import filepath, check_args


@check_args
def _process_cmd(args):

    output_csvfile = filepath(args.output_csvfile, args.input_swcfile, format = 'csv', suffix = 'info') 
    output_swcfile = filepath(args.output_swcfile, args.input_swcfile, format = 'swc', suffix = 'info')
    return args.input_swcfile, output_csvfile, output_swcfile


def _args_to_check(args):
    vars(args)['check'] = {}
    args.check['input_swc'] = [args.input_swcfile, 'swc']


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('input_swcfile')
    parser.add_argument('-c', '--output_csvfile', action = 'store', default = r'./',
                        help = 'output csv filename of directory')
    parser.add_argument('-s', '--output_swcfile', action = 'store', default = r'./',
                        help = 'output swc filename of directory')
    args = parser.parse_args()
    _args_to_check(args)

    input_swcfile, output_csvfile, output_swcfile = _process_cmd(args)

    swc__csv_swc(input_swcfile, csv = output_csvfile, swc = output_swcfile)
    print('Successfully created %s!\nSuccessfully created %s!'%(output_csvfile, output_swcfile))


if __name__ == '__main__':
    main()


