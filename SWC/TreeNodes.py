
def AllTreeNodes(tree):
	return (tree, ) + tree.descendants


def TreeLeaves(tree):
    return (leaf for child in tree.children for leaf in TreeLeaves(child)) if not tree.is_leaf else (tree,)