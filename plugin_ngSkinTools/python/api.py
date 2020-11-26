
# IMPORTS --------------------------------------------------------------------------------------- #
from maya import cmds, mel
from ngSkinTools.mllInterface import MllInterface
from ngSkinTools.paint import ngLayerPaintCtxInitialize
from ngSkinTools.utils import Utils

from .core import adjust, paint, component
# ----------------------------------------------------------------------------------------------- #


# ----------------------------------------------------------------------------------------------- #
class NgPaintStroke():
    """ Custom ngSkinTools brush setup class """

    MODE      = 1
    VALUE     = 1
    STROKE_ID = None

    def __init__(self, surface):
        self.surface = surface
        self.selection = cmds.ls(selection=True)[0]
        self.mesh = cmds.listRelatives(self.selection, shapes=True)[0]

        self.mll = MllInterface()
        self.ngs_layer_id = self.mll.getCurrentLayer()
        self.ngs_target = self.mll.getCurrentPaintTarget()
        self.ngs_weight_list = self.mll.getInfluenceWeights(self.ngs_layer_id, self.ngs_target)

    def stroke_initialize(self):
        """ Executes before each brushstroke """
        cmds.undoInfo(openChunk=True, undoName="custom_ngPaintStroke")
        cmds.ngSkinLayer(paintOperation=self.MODE, paintIntensity=self.VALUE)

        stroke_id_str  = ngLayerPaintCtxInitialize(self.mesh)
        self.stroke_id = int(stroke_id_str.split(" ")[1])

        return self.surface, self.stroke_id

    def paint_contrast(self, vtxID, value):
        """ sharpen edge of active weight map on brushstroke """
        min_weight = min(self.ngs_weight_list)
        max_weight = max(self.ngs_weight_list)
        weight = self.ngs_weight_list[vtxID]

        if not max_weight > weight > min_weight:
            return  # skip weights with no change

        result = paint.contrast(value, weight, min_weight, max_weight)
        cmds.ngSkinLayer(paintIntensity=result)
        cmds.ngLayerPaintCtxSetValue(self.stroke_id, vtxID, 1)

    def paint_gain(self, vtxID, value):
        """ increase weight intensity, preserving zero weights """
        weight = self.ngs_weight_list[vtxID]

        if weight == 0:
            return # skip zero weights

        result = paint.gain(value, weight)
        cmds.ngSkinLayer(paintIntensity=result)
        cmds.ngLayerPaintCtxSetValue(self.stroke_id, vtxID, 1)

    def stroke_finalize(self):
        """ Executes after each brushstroke """
        if self.stroke_id:
            cmds.ngLayerPaintCtxFinalize(self.stroke_id)
        self.stroke_id = None
        cmds.undoInfo(closeChunk=True)
# ----------------------------------------------------------------------------------------------- #


# ----------------------------------------------------------------------------------------------- #
class NgMapAdjustment():
    """ Custom operations applied onto entire active ngSkinTools layer """

    def __init__(self):
        pass
# ----------------------------------------------------------------------------------------------- #