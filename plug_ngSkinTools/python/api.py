
# IMPORTS --------------------------------------------------------------------------------------- #
import os

from maya import cmds, mel
from ngSkinTools.mllInterface import MllInterface
from ngSkinTools.paint import ngLayerPaintCtxInitialize
from ngSkinTools.utils import Utils

from .core import adjust, paint
# ----------------------------------------------------------------------------------------------- #


MEL_SCRIPT = r'mel/brush_utilities.mel'
COMMANDS = {
    'test'    : 'ngSkinToolsCustom_Test',
    'conceal' : 'ngSkinToolsCustom_Conceal',
    'spread'  : 'ngSkinToolsCustom_Spread',
    'contrast': 'ngSkinToolsCustom_Contrast',
    'gain'    : 'ngSkinToolsCustom_Gain',
    'equalize': 'ngSkinToolsCustom_VolEq'
}


# ----------------------------------------------------------------------------------------------- #
class NgPaintStroke():
    """ Custom ngSkinTools brush setup class """

    MODE      = 1
    VALUE     = 1
    STROKE_ID = None

    def __init__(self, surface):
        self.surface = surface

        self.mll             = MllInterface()
        self.ngs_layer_id    = self.mll.getCurrentLayer()
        self.ngs_target      = self.mll.getCurrentPaintTarget()
        self.ngs_target_info = self.mll.getTargetInfo()
        self.ngs_weight_list = self.mll.getInfluenceWeights(self.ngs_layer_id, self.ngs_target)

    def stroke_initialize(self):
        """ Executes before each brushstroke """
        cmds.undoInfo(openChunk=True, undoName="custom_ngPaintStroke")
        cmds.ngSkinLayer(paintOperation=self.MODE, paintIntensity=self.VALUE)

        stroke_id_str  = ngLayerPaintCtxInitialize(self.ngs_target_info[0])
        self.STROKE_ID = int(stroke_id_str.split(" ")[1])

        return self.surface, self.STROKE_ID

    def paint_contrast(self, vtxID, value):
        """ sharpen edge of active weight map on brushstroke """
        min_weight = min(self.ngs_weight_list)
        max_weight = max(self.ngs_weight_list)
        weight = self.ngs_weight_list[vtxID]

        if not max_weight > weight > min_weight:
            return  # skip weights with no change

        result = paint.contrast(value, weight, min_weight, max_weight)
        cmds.ngSkinLayer(paintIntensity=result)
        cmds.ngLayerPaintCtxSetValue(self.STROKE_ID, vtxID, 1)

    def paint_gain(self, vtxID, value):
        """ increase weight intensity, preserving zero weights """
        weight = self.ngs_weight_list[vtxID]

        if weight == 0:
            return # skip weights with no change

        result = paint.gain(value, weight)
        cmds.ngSkinLayer(paintIntensity=result)
        cmds.ngLayerPaintCtxSetValue(self.STROKE_ID, vtxID, 1)

    def paint_test(self, vtxID, value):
        """ test input of the brush scripts """
        print('surface: ', self.surface)
        print('target:  ', self.mll.getTargetInfo())
        print('vertex:  ', vtxID, value)

    def stroke_finalize(self):
        """ Executes after each brushstroke """
        if self.STROKE_ID:
            cmds.ngLayerPaintCtxFinalize(self.STROKE_ID)
        self.STROKE_ID = None
        cmds.undoInfo(closeChunk=True)
# ----------------------------------------------------------------------------------------------- #


# ----------------------------------------------------------------------------------------------- #
class NgMapAdjustment():
    """ Custom operations applied onto entire active ngSkinTools layer """
    def __init__(self):
        pass
# ----------------------------------------------------------------------------------------------- #


# ----------------------------------------------------------------------------------------------- #
class NgComponent():
    """ Custom operations applied to selected components """
    def __init__(self):
        pass
# ----------------------------------------------------------------------------------------------- #


# SCRIPT BRUSH SETUP ---------------------------------------------------------------------------- #
def custom_paint_setup():
    package_path = os.path.dirname(os.path.dirname(__file__))
    mel_cmd = 'source "{}"'.format(os.path.join(package_path, MEL_SCRIPT).replace('\\', '/'))
    mel.eval(mel_cmd)
    cmds.artUserPaintCtx(
        "ngSkinToolsLayerPaintCtx",
        initializeCmd="ngSkinToolsCustom_Initialize",
        finalizeCmd="ngSkinToolsCustom_Finalize",
        e=True,
    )

def custom_paint_value(valueCommand):
    cmds.artUserPaintCtx(
        "ngSkinToolsLayerPaintCtx",
        setValueCommand=COMMANDS[valueCommand],
        e=True
    )

def custom_paint_exit():
    init_cmd = Utils.createMelProcedure(ngLayerPaintCtxInitialize, [('string', 'mesh')], returnType='string')
    cmds.artUserPaintCtx(
        "ngSkinToolsLayerPaintCtx",
        setValueCommand="ngLayerPaintCtxSetValue",
        initializeCmd=init_cmd,
        finalizeCmd="ngLayerPaintCtxFinalize",
        value=1,
        e=True
    )
# ----------------------------------------------------------------------------------------------- #
