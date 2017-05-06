#!/usr/bin/env python
#coding: utf-8

from TreeNodes import AllTreeNodes

def TreeParaRescale(tree, **dict):
	all_nodes = AllTreeNodes(tree)
	for para in ('x', 'y', 'z', 'r'):
		if para in dict:
			map(lambda node: node.para_rescale(para, dict[para]), all_nodes)
