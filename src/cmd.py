#!/usr/bin/env python
#coding: utf-8

import os
import warnings
import functools


def filepath(file, default_name, format = '', suffix = ''):
    
    filepath = file

    default_name = '.'.join(os.path.split(default_name)[1].split('.')[:-1])
    
    if format and not format.startswith('.'):
        format = '.' + format

    if suffix and not suffix.startswith('_'):
        suffix = '_' + suffix 

    if not filepath.endswith(format):
        if not os.path.isdir(filepath):
            os.makedirs(filepath)
        filepath = os.path.join(filepath, default_name + suffix + format)

    else:
        if not os.path.isdir(os.path.split(filepath)[0]):
            os.makedirs(os.path.split(filepath)[0])

    return filepath

################################################################

def _check_format(file, format, format_case_sensitive = False):    
    
    if not format.startswith('.'):
        format = '.' + format

    if not format_case_sensitive:
        if not file.lower().endswith(format):
            raise IOError('Wrong input format: {file} ({format} file is expected)'.format(file = file, format = format))
    else:
        if not file.endswith(format):
            raise IOError('Wrong input format: {file} ({format} file is expected)'.format(file = file, format = format))
  

def _check_existence(filepath):
    import os
    if not os.path.isfile(filepath):
        raise IOError('File does not exists: {file}'.format(file = filepath))
 

def check_file(file, format, file_type = None, format_case_sensitive = False):
    if not file:
        if file_type:
            raise Exception('{filetype} is needed!'.format(filetype = file_type))
        else:
            raise Exception('File missed!')
    _check_format(file, format, format_case_sensitive)
    _check_existence(file)


def check_args(func):
    @functools.wraps(func)
    def wrapper(args):
        try:
            for argname in args.check.keys():
                check_file(*(args.check[argname]+[argname,]))
        except AttributeError:
            warnings.warn('No arguments to check.')

        return func(args)

    return wrapper