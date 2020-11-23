"""
    Component level operations
"""


# ----------------------------------------------------------------------------------------------- #
# IMPORTS
from maya import cmds
from maya.api import OpenMaya
# ----------------------------------------------------------------------------------------------- #


# ----------------------------------------------------------------------------------------------- #
# UTILITIES
def adjacent_vtx(vertex):
    """ returns a list of vertex indices that are connected by edge with the input vertex """
    edge_list = cmds.polyListComponentConversion(vertex, toEdge=True)
    vertex_list = cmds.polyListComponentConversion(edge_list, toVertex=True)
    vertex_list = cmds.ls(vertex_list, flatten=True)
    id_list = list(map(lambda x: x[x.find("[") + 1:x.find("]")], vertex_list))
    return id_list
# ----------------------------------------------------------------------------------------------- #
