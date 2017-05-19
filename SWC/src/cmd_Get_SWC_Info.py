#!/usr/bin/env python
#coding: utf-8

import os
import argparse

from Get_SWC_Info import SWC_CSVorSWC


def get_output(output_csv, output_swc, default_name):
    output_csvfile = output_csv    
    output_swcfile = output_swc   
    if not output_csvfile.endswith('.csv'):
        if not os.path.isdir(output_csvfile):
            os.makedirs(output_csvfile)
        output_csvfile = os.path.join(output_csvfile, os.path.split(default_name)[1][:-4]+'_info.csv')
    else:
        if not os.path.isdir(os.path.split(output_csvfile)[0]):
            os.makedirs(os.path.split(output_csvfile)[0])
    
    if not output_swcfile.endswith('.swc'):
        if not os.path.isdir(output_swcfile):
            os.makedirs(output_swcfile)
        output_swcfile = os.path.join(output_swcfile, os.path.split(default_name)[1][:-4]+'_info.swc')
    else:
        if not os.path.isdir(os.path.split(output_swcfile)[0]):
            os.makedirs(os.path.split(output_swcfile)[0])
    
    return output_csvfile, output_swcfile



def process_cmd(input_swcfile, output_csv, output_swc):
    if not os.path.isfile(input_swcfile):
        IOError('{} does not exists!'.format(input_swcfile))

    output_csvfile, output_swcfile = get_output(output_csv, output_swc, input_swcfile)
    return input_swcfile, output_csvfile, output_swcfile


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('input_swcfile')
    parser.add_argument('-c', '--output_csvfile', action = 'store', default = r'./',
                        help = 'output csv filename of directory')
    parser.add_argument('-s', '--output_swcfile', action = 'store', default = r'./',
                        help = 'output swc filename of directory')
    args = parser.parse_args()

    input_swcfile, output_csvfile, output_swcfile = process_cmd(args.input_swcfile, args.output_csvfile, args.output_swcfile)

    SWC_CSVorSWC(input_swcfile, csv = output_csvfile, swc = output_swcfile)
    print('Successfully created %s!\nSuccessfully created %s!'%(output_csvfile, output_swcfile))


if __name__ == '__main__':
    main()


