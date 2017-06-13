#!/usr/bin/env python
#coding: utf-8

import functools

def ele_mani(func):
    
    @functools.wraps(func)
    def wrapper(list, *args, **dict):
        try:
            return map(lambda x: func(x, *args, **dict), list)
        
        except TypeError:
            return func(list, *args, **dict)
    
    return wrapper
