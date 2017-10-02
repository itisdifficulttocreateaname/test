#!/usr/bin/env python
#coding: utf-8

import csv

from Get_SWC_Info import swc_forest
from StretchType import stretch_type
from Radius_Change import mark_all_ders
from ele_manipulation import ele_mani

def is_swollen(node, mode = 'type', *range):
    ## RANGE can be a list of real numbers 
    ## and will be recognized as a series of intervals
    ## MODE can be 'type' or 'derivative', refers to 
    ## 'stretched type' or 'second-order-derivative',
    ## specifing the parameter that the range determines.
    ## Output will be true iff the type or der of node falls in range.

    if mode == 'type':
        for index, threshold in enumerate(range):
            if (index%2 == 0 and node.type < threshold) or not node.is_der_loc_min:
                return False
            if (index%2 == 1 and node.type > threshold) or not node.is_der_loc_min:
                return False
        return True 

    elif mode == 'derivative':
        for index, threshold in enumerate(range):
            if (index%2 == 0 and node.der < threshold) or not node.is_der_loc_min:
                return False
            if (index%2 == 1 and node.der > threshold) or not node.is_der_loc_min:
                return False
        return True 
    else:
        raise Exception("'mode' should be 'type' or 'derivative'!")


def swollen_id(tree, mode = 'type', *range):
    swollen_id = []
    for node in tree.all_nodes:
        if is_swollen(node, mode, *range):
            swollen_id.append(node.id)
    return swollen_id


def swc_swollenID_csv(swc_filename, csv_filename, mode = 'type', *range):
    forest = swc_forest(swc_filename)

    with open(csv_filename, 'wb') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter = ',', quotechar = '|', quoting = csv.QUOTE_MINIMAL)
        spamwriter.writerow(['Swollen Id'])
        for tree in forest:
            swollenid = swollen_id(tree, mode, *range)
            map(lambda x: spamwriter.writerow([x,]), swollenid)




