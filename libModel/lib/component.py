"""
    Component level operations
"""


# IMPORTS --------------------------------------------------------------------------------------- #
from maya import cmds
from maya.api import OpenMaya
# ----------------------------------------------------------------------------------------------- #


# VERTEX ---------------------------------------------------------------------------------------- #
def connected_vertices(vertex):
    """
    find vertices that are connected by edge with the given vertex.

    :param vertex:    MObject or dagPath of the given vertex
                       - MObject(component)
                       - "surface.vtx[id]"

    :return vertices: MayaIntArray of vertex IDs
                       - MayaIntArray[int, int, ...]
    """
    selectionList = OpenMaya.MSelectionList()
    selectionList.add(vertex)
    meshObject, vertexComponent = selectionList.getComponent(0)

    vtxIterator = OpenMaya.MItMeshVertex(meshObject, vertexComponent)
    return vtxIterator.getConnectedVertices()


def connected_edges(vertex):
    raise NotImplementedError


def connected_faces(vertex):
   raise NotImplementedError

# ----------------------------------------------------------------------------------------------- #