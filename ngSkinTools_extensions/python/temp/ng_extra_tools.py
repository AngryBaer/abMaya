"""

    this module adds three custom paint operations to the ng skin tools plugin UI

        these operations include:
         - retract
         - spread
         - contrast
         - gain
         - volume equalize

        additionally there are the following options for modifying the entire weight map:
         - shrink map
         - grow map
         - flood brush

    Author: Alexander Baehr, 2017

"""

import maya.cmds as cmds
import maya.mel as mel
import ng_equalizer as eq
from math import pow
from math import sqrt
from scipy.stats import norm
from ngSkinTools.mllInterface import MllInterface
from ngSkinTools.utils import Utils
from ngSkinTools.paint import ngLayerPaintCtxInitialize


def get_target_control(ui_path):
    """ returns a list of controls or layouts within a specified ui path """
    UI_list = cmds.lsUI(type=['control', 'controlLayout', 'menu'], long=True)
    target_control = ui_path.split('|')
    number_list = []
    for items in UI_list:
        layouts = items.split('|')
        number = ''.join(i for i in layouts[-1] if i.isdigit())
        target_items = ''.join(i for i in items if not i.isdigit())
        if target_items == ui_path:
            number_list.append(int(number))
    if number_list:
        target_list = [''.join([target_control[-1], str(i)]) for i in sorted(number_list)]
        return target_list


def get_surrounding_verts(vertex):
    """ returns a list of vertex indices that are connected by edge with the input vertex """
    edge_list = cmds.polyListComponentConversion(vertex, toEdge=True)
    vertex_list = cmds.polyListComponentConversion(edge_list, toVertex=True)
    vertex_list = cmds.ls(vertex_list, flatten=True)
    id_list = list(map(lambda x: x[x.find("[") + 1:x.find("]")], vertex_list))
    return id_list


class UseNgBrush(object):
    """ setup for custom brush operations, a new instance is created on every brush stroke """
    def __init__(self, surface_name):
        self.surface = surface_name
        self.stroke_id = None
        self.mode = 1
        self.value = 1
        self.volumeThreshold = -0.1

        self.mll = MllInterface()
        self.selection_name = cmds.ls(selection=True)
        self.mesh = cmds.listRelatives(self.selection_name[0], shapes=True)
        self.ngs_layer_id = self.mll.getCurrentLayer()
        self.ngs_influence = self.mll.getCurrentPaintTarget()
        self.ngs_weight_list = self.mll.getInfluenceWeights(self.ngs_layer_id, self.ngs_influence)
        self.max_value = max(self.ngs_weight_list)
        self.min_value = min(self.ngs_weight_list)

    def stroke_initialize(self):
        """ this function is executed before each brush stroke """
        cmds.undoInfo(openChunk=True, undoName="paint stroke")
        get_stroke_id = ngLayerPaintCtxInitialize(self.mesh[0])
        self.stroke_id = int(get_stroke_id.split(" ")[1])
        cmds.ngSkinLayer(paintOperation=self.mode, paintIntensity=self.value)
        self.stroke_update()
        return self.surface, self.stroke_id

    def stroke_finalize(self):
        """ this function is executed after each brush stroke """
        if self.stroke_id:
            cmds.ngLayerPaintCtxFinalize(self.stroke_id)
        self.stroke_id = None
        cmds.undoInfo(closeChunk=True)

    def stroke_update(self):
        """ updates certain attributes for the brush instance """
        # self.mll = MllInterface()
        # self.selection_name = cmds.ls(selection=True)
        # self.mesh = cmds.listRelatives(self.selection_name[0], shapes=True)
        # self.ngs_layer_id = self.mll.getCurrentLayer()
        # self.ngs_influence = self.mll.getCurrentPaintTarget()
        # self.ngs_weight_list = self.mll.getInfluenceWeights(self.ngs_layer_id, self.ngs_influence)
        # self.max_value = max(self.ngs_weight_list)
        # self.min_value = min(self.ngs_weight_list)
        self.volumeThreshold = cmds.floatSlider("volume_slider", q=True, value=True)

    def contrast_paint(self, vert_id, value):
        """ sharpens the edge of the active weight map """
        vertex_weight = self.ngs_weight_list[vert_id]
        if not self.max_value > vertex_weight > self.min_value:
            return
        avg_value = (self.max_value + self.min_value) / 2
        normalized_range = self.max_value - self.min_value
        dist_value = vertex_weight - avg_value
        modifier = norm.cdf(dist_value, loc=0, scale=(0.1 * normalized_range)) - vertex_weight
        contrast_weight = vertex_weight + (modifier * value)
        contrast_weight = max(self.min_value, min(contrast_weight, self.max_value))
        cmds.ngSkinLayer(paintIntensity=contrast_weight)
        cmds.ngLayerPaintCtxSetValue(self.stroke_id, vert_id, 1)

    def retract_paint(self, vert_id, value):
        """ smooth operation that only lowers weight values """
        vertex_weight = self.ngs_weight_list[vert_id]
        if vertex_weight <= self.min_value:
            return
        vertex_name = '.'.join([self.selection_name[0], 'vtx[%d]' % vert_id])
        area_vertices = get_surrounding_verts(vertex_name)
        weight_list = [self.ngs_weight_list[int(x)] for x in area_vertices]
        weight_avg = sum(weight_list) / float(len(weight_list))
        min_avg = min(weight_list)
        threshold = 0.01 / (value / 0.1)
        if weight_avg >= self.max_value and abs(weight_avg - vertex_weight) <= threshold:
            return
        weight_diff = abs(weight_avg - vertex_weight)
        retract_weight = vertex_weight * (1 - (weight_diff * value))
        retract_weight = max(retract_weight, min_avg)
        cmds.ngSkinLayer(paintIntensity=retract_weight)
        cmds.ngLayerPaintCtxSetValue(self.stroke_id, vert_id, 1)

    def spread_paint(self, vert_id, value):
        """ smooth operation that only increases weight values """
        vertex_weight = self.ngs_weight_list[vert_id]
        if vertex_weight >= self.max_value:
            return
        vertex_name = '.'.join([self.selection_name[0], 'vtx[%d]' % vert_id])
        area_vertices = get_surrounding_verts(vertex_name)
        weight_list = [self.ngs_weight_list[int(x)] for x in area_vertices]
        weight_avg = sum(weight_list) / float(len(weight_list))
        max_avg = max(weight_list)
        threshold = 0.01 / (value / 0.1)
        if weight_avg <= self.min_value and abs(weight_avg - vertex_weight) <= threshold:
            return
        weight_diff = abs(weight_avg - vertex_weight)
        spread_weight = vertex_weight + (weight_diff * value)
        spread_weight = min(spread_weight, max_avg)
        cmds.ngSkinLayer(paintIntensity=spread_weight)
        cmds.ngLayerPaintCtxSetValue(self.stroke_id, vert_id, 1)

    def gain_paint(self, vert_id, value):
        """ increases existing weight values but preserves empty weights """
        vertex_weight = self.ngs_weight_list[vert_id]
        if vertex_weight == 0:
            return
        gain_weight = vertex_weight + (vertex_weight * value)
        gain_weight = min(gain_weight, 1)
        cmds.ngSkinLayer(paintIntensity=gain_weight)
        cmds.ngLayerPaintCtxSetValue(self.stroke_id, vert_id, 1)

    def volume_equalize(self, vert_id, value):
        """
        i.e a volumetric match operation with a falloff.
        applies weight values inside the brush radius onto other vertices inside a spherical volume
        """
        origin_vertex = '.'.join([self.selection_name[0], 'vtx[%s]']) % vert_id
        vertex_weight = self.ngs_weight_list[vert_id]
        v1 = cmds.pointPosition(origin_vertex)
        for i in range(len(self.ngs_weight_list)):
            target_weight = self.ngs_weight_list[i]
            if target_weight == vertex_weight:
                continue
            if i == vert_id:
                continue
            target_vertex = '.'.join([self.selection_name[0], 'vtx[%s]']) % i
            v2 = cmds.pointPosition(target_vertex)
            target_distance = sqrt(
                (pow((v1[0]-v2[0]), 2)) +
                (pow((v1[1]-v2[1]), 2)) +
                (pow((v1[2]-v2[2]), 2))
            )
            if target_distance > (self.volumeThreshold * value):
                continue
            falloff = (self.volumeThreshold - target_distance) / self.volumeThreshold
            eq_weight = target_weight - (((target_weight - vertex_weight) * value) * falloff)
            cmds.ngSkinLayer(paintIntensity=eq_weight)
            cmds.ngLayerPaintCtxSetValue(self.stroke_id, i, 1)


class MapOperations(object):
    """ class that contains operations applied to the entire mesh """

    def __init__(self):
        self.mll = MllInterface()
        self.selection_name = []
        self.ngs_layer_id = -1
        self.ngs_influence = None
        self.ngs_weight_list = []
        self.ngs_vert_count = -1
        self.max_value = -1.0
        self.min_value = -1.0

    def get_data(self):
        self.selection_name = cmds.ls(selection=True)
        self.ngs_layer_id = self.mll.getCurrentLayer()
        self.ngs_influence = self.mll.getCurrentPaintTarget()
        self.ngs_weight_list = self.mll.getInfluenceWeights(self.ngs_layer_id, self.ngs_influence)
        self.ngs_vert_count = self.mll.getVertCount()
        self.max_value = max(self.ngs_weight_list)
        self.min_value = min(self.ngs_weight_list)

    def grow_map(self, intensity):
        """ pushes the border of the active weight map outwards """
        self.get_data()
        new_weight_list = []
        for i in range(self.ngs_vert_count):
            vertex_weight = self.ngs_weight_list[i]
            if vertex_weight >= self.max_value:
                new_weight_list.append(vertex_weight)
                continue
            vertex_name = '.'.join([self.selection_name[0], 'vtx[%d]' % i])
            area_vertices = get_surrounding_verts(vertex_name)
            weight_list = [self.ngs_weight_list[int(x)] for x in area_vertices]
            max_avg = max(weight_list)
            if max_avg <= self.min_value:
                new_weight_list.append(vertex_weight)
                continue
            grow_weight = vertex_weight + (abs(vertex_weight - max_avg) * intensity)
            grow_weight = min(grow_weight, self.max_value)
            new_weight_list.append(grow_weight)
        self.mll.setInfluenceWeights(self.ngs_layer_id, self.ngs_influence, new_weight_list)

    def shrink_map(self, intensity):
        """ pulls the border of the active weight map inwards """
        self.get_data()
        new_weight_list = []
        for i in range(self.ngs_vert_count):
            vertex_weight = self.ngs_weight_list[i]
            if vertex_weight <= self.min_value:
                new_weight_list.append(vertex_weight)
                continue
            vertex_name = '.'.join([self.selection_name[0], 'vtx[%d]' % i])
            area_vertices = get_surrounding_verts(vertex_name)
            weight_list = [self.ngs_weight_list[int(x)] for x in area_vertices]
            min_avg = min(weight_list)
            if min_avg >= self.max_value:
                new_weight_list.append(vertex_weight)
                continue
            shrink_weight = vertex_weight - (abs(vertex_weight - min_avg) * intensity)
            shrink_weight = max(shrink_weight, self.min_value)
            new_weight_list.append(shrink_weight)
        self.mll.setInfluenceWeights(self.ngs_layer_id, self.ngs_influence, new_weight_list)

    def retract_map(self, intensity):
        """ smooth operation for the active map by only lowering values """
        self.get_data()
        new_weight_list = []
        threshold = 0.01 / (intensity / 0.1)
        for i in range(self.ngs_vert_count):
            vertex_weight = self.ngs_weight_list[i]
            if vertex_weight <= self.min_value:
                new_weight_list.append(vertex_weight)
                continue
            vertex_name = '.'.join([self.selection_name[0], 'vtx[%d]' % i])
            area_vertices = get_surrounding_verts(vertex_name)
            weight_list = [self.ngs_weight_list[int(x)] for x in area_vertices]
            weight_avg = sum(weight_list) / float(len(weight_list))
            min_avg = min(weight_list)
            if weight_avg >= self.max_value and abs(weight_avg - vertex_weight) < threshold:
                new_weight_list.append(vertex_weight)
                continue
            weight_diff = abs(weight_avg - vertex_weight)
            retract_weight = vertex_weight * (1 - (weight_diff * intensity))
            retract_weight = max(retract_weight, min_avg)
            new_weight_list.append(retract_weight)
        self.mll.setInfluenceWeights(self.ngs_layer_id, self.ngs_influence, new_weight_list)

    def spread_map(self, intensity):
        """ smooth operation for the active map by only increasing values """
        self.get_data()
        new_weight_list = []
        threshold = 0.01 / (intensity / 0.1)
        for i in range(self.ngs_vert_count):
            vertex_weight = self.ngs_weight_list[i]
            if vertex_weight >= self.max_value:
                new_weight_list.append(vertex_weight)
                continue
            vertex_name = '.'.join([self.selection_name[0], 'vtx[%d]' % i])
            area_vertices = get_surrounding_verts(vertex_name)
            weight_list = [self.ngs_weight_list[int(x)] for x in area_vertices]
            weight_avg = sum(weight_list) / float(len(weight_list))
            max_avg = max(weight_list)
            if weight_avg <= self.min_value and abs(weight_avg - vertex_weight) < threshold:
                new_weight_list.append(vertex_weight)
                continue
            weight_diff = abs(weight_avg - vertex_weight)
            spread_weight = vertex_weight + weight_diff * intensity
            spread_weight = min(spread_weight, max_avg)
            new_weight_list.append(spread_weight)
        self.mll.setInfluenceWeights(self.ngs_layer_id, self.ngs_influence, new_weight_list)

    def gain_map(self, intensity):
        """ 'reverse scale' tool that only increases weight values above 0 """
        self.get_data()
        new_weight_list = []
        for i in range(self.ngs_vert_count):
            vertex_weight = self.ngs_weight_list[i]
            if vertex_weight == 0:
                new_weight_list.append(vertex_weight)
                continue
            gain_weight = vertex_weight + (vertex_weight * intensity)
            gain_weight = min(gain_weight, 1)
            new_weight_list.append(gain_weight)
        self.mll.setInfluenceWeights(self.ngs_layer_id, self.ngs_influence, new_weight_list)

    def contrast_map(self, intensity):
        """ sharpens the edge of the active weight map """
        self.get_data()
        new_weight_list = []
        avg_value = (self.max_value + self.min_value) / 2
        normalized_range = self.max_value - self.min_value
        for i in range(self.ngs_vert_count):
            vertex_weight = self.ngs_weight_list[i]
            if not self.max_value > vertex_weight > self.min_value:
                new_weight_list.append(vertex_weight)
                continue
            dist_value = vertex_weight - avg_value
            modifier = norm.cdf(dist_value, loc=0, scale=(0.1 * normalized_range)) - vertex_weight
            contrast_weight = vertex_weight + modifier * intensity
            contrast_weight = max(self.min_value, min(contrast_weight, self.max_value))
            new_weight_list.append(contrast_weight)
        self.mll.setInfluenceWeights(self.ngs_layer_id, self.ngs_influence, new_weight_list)


class PaintExtras(object):
    """ adds a custom Formlayout inside the Paint Tab of the ngSkinTools UI """

    def __init__(self):
        self.mll = MllInterface()
        self.ng_color_set = ""
        self.check_color_set = 'checkSetBlue'
        self.mo = MapOperations()
        self.radio_text = 'Mode:'
        self.retract = 'Retract'
        self.spread = 'Spread'
        self.contrast = 'Contrast'
        self.gain = "Gain"
        self.volume = "Volume EQ"
        self.defaultOp = 'Retract'
        self.select_mode = True
        self.intensityField = 'Intensity'
        self.defaultVal = 1
        self.shrinkButton = 'Shrink Map'
        self.growButton = 'Grow Map'
        self.floodButton = 'Quick Flood'
        self.exitButton = 'Exit Tool'
        self.matchButton = 'Match Brush'

        self.dividerEQ = "dividerEQ"
        self.editMenuEQ = 'Vertex Equalizer Tool'

        self.extra_check = "Use Extra Brushes"
        self.extra_frame = "Extra Tools"
        self.radio_form = "radio_form"
        self.intensity_label = "Intensity:"
        self.volume_label = "Volume:"
        self.intensity_row = "intensity_row"
        self.volume_row = "threshold_row"
        self.extra_field = "extra_field"
        self.extra_slider = "extra_slider"
        self.volume_field = "volume_field"
        self.volume_slider = "volume_slider"
        self.mode_collection = "mode_collection"
        self.button_form = "button_form"
        # self.brush_display_check = "Draw Brush while painting"
        # self.default_brush_display = cmds.artUserPaintCtx(outwhilepaint=True, q=True)

        self.ui_paths = {
            "paint_tab": "MayaWindow|horizontalSplit|tabLayout|formLayout|scrollLayout|columnLayout",
            "paint_buttons": "MayaWindow|horizontalSplit|tabLayout|formLayout|formLayout|button",
            "mode_radio": "MayaWindow|horizontalSplit|tabLayout|formLayout|scrollLayout|columnLayout|frameLayout"
                          "|columnLayout|formLayout|rowColumnLayout|radioButton",
            "mode_layout": "MayaWindow|horizontalSplit|tabLayout|formLayout|scrollLayout|columnLayout"
                           "|frameLayout|columnLayout|formLayout|rowColumnLayout",
            "intensity_slider": "MayaWindow|horizontalSplit|tabLayout|formLayout|scrollLayout|columnLayout|frameLayout"
                                "|columnLayout|formLayout|rowLayout|floatSlider",
            "slider_rows": "MayaWindow|horizontalSplit|tabLayout|formLayout|scrollLayout|columnLayout|frameLayout"
                           "|columnLayout|formLayout|rowLayout",
            "checkboxes": "MayaWindow|horizontalSplit|tabLayout|formLayout|scrollLayout|columnLayout|frameLayout"
                          "|columnLayout|formLayout|columnLayout|checkBox",
            "EA_menu": "MayaWindow|horizontalSplit|formLayout|menuBarLayout|menu"
        }

        self.ng_radio_layout = get_target_control(self.ui_paths["mode_layout"])
        self.ng_radio_buttons = get_target_control(self.ui_paths["mode_radio"])
        self.ng_intensity = get_target_control(self.ui_paths["intensity_slider"])
        self.ng_checkboxes = get_target_control(self.ui_paths["checkboxes"])
        self.ng_slider_rows = get_target_control(self.ui_paths["slider_rows"])
        self.ng_paint_buttons = get_target_control(self.ui_paths["paint_buttons"])
        self.ng_menu = get_target_control(self.ui_paths["EA_menu"])

    def paint_tool_setup(self, *args):
        """ changes the initial settings for the paint script tool """
        cmds.rowColumnLayout(self.ng_radio_layout[0], e=True, enable=False)
        cmds.checkBox(self.ng_checkboxes[0], e=True, enable=False)
        cmds.checkBox(self.ng_checkboxes[1], e=True, enable=False)
        cmds.rowLayout(self.ng_slider_rows[0], e=True, enable=False)
        cmds.formLayout(self.radio_form, e=True, enable=True)
        cmds.button(self.floodButton, e=True, enable=True)
        cmds.rowLayout(self.intensity_row, e=True, enable=True)

        cmds.artUserPaintCtx(
            "ngSkinToolsLayerPaintCtx",
            e=True,
            initializeCmd="ngSkinAlexUtilInitialize",
            finalizeCmd="ngSkinAlexUtilFinalize",
        )
        self.intensity()
        self.match_volume()
        self.paint_mode()

    def paint_mode(self, *args):
        """ replaces the set value MEL script in the paint script tool """
        paint_mode = cmds.radioCollection(self.mode_collection, q=True, select=True)
        cmds.rowLayout(self.volume_row, e=True, enable=False)
        cmds.button(self.floodButton, e=True, enable=True)
        if paint_mode == "retract_radio":
            cmds.artUserPaintCtx("ngSkinToolsLayerPaintCtx", e=True, setValueCommand="ngSkinAlexUtilRetract")
        if paint_mode == "spread_radio":
            cmds.artUserPaintCtx("ngSkinToolsLayerPaintCtx", e=True, setValueCommand="ngSkinAlexUtilSpread")
        if paint_mode == "contrast_radio":
            cmds.artUserPaintCtx("ngSkinToolsLayerPaintCtx", e=True, setValueCommand="ngSkinAlexUtilContrast")
        if paint_mode == "gain_radio":
            cmds.artUserPaintCtx("ngSkinToolsLayerPaintCtx", e=True, setValueCommand="ngSkinAlexUtilGain")
        if paint_mode == "volume_radio":
            cmds.artUserPaintCtx("ngSkinToolsLayerPaintCtx", e=True, setValueCommand="ngSkinAlexUtilVolEq")
            cmds.rowLayout(self.volume_row, e=True, enable=True)
            cmds.button(self.floodButton, e=True, enable=False)

    def intensity(self, *args):
        """ sets the value slider of the paint script tool to this amount """
        intensity = cmds.floatSlider(self.extra_slider, q=True, value=True)
        cmds.artUserPaintCtx("ngSkinToolsLayerPaintCtx", e=True, value=intensity)

    def flood(self, *args):
        """ applies selected operation to the entire mesh """
        intensity = cmds.floatSlider(self.extra_slider, q=True, value=True)
        paint_mode = cmds.radioCollection(self.mode_collection, q=True, select=True)
        if paint_mode == "retract_radio":
            self.mo.retract_map(intensity)
        if paint_mode == "spread_radio":
            self.mo.spread_map(intensity)
        if paint_mode == "contrast_radio":
            self.mo.contrast_map(intensity)
        if paint_mode == "gain_radio":
            self.mo.gain_map(intensity)

    def grow(self, *args):
        """ starts the grow map operation """
        intensity = cmds.floatSlider(self.ng_intensity[0], q=True, value=True)
        if cmds.checkBox(self.extra_check, q=True, value=True):
            intensity = cmds.floatSlider(self.extra_slider, q=True, value=True)
        self.mo.grow_map(intensity)

    def shrink(self, *args):
        """ starts the shrink map operation """
        intensity = cmds.floatSlider(self.ng_intensity[0], q=True, value=True)
        if cmds.checkBox(self.extra_check, q=True, value=True):
            intensity = cmds.floatSlider(self.extra_slider, q=True, value=True)
        self.mo.shrink_map(intensity)

    def update_float_field(self, *args):
        float_intensity = cmds.floatSlider(self.extra_slider, q=True, value=True)
        volume_intensity = cmds.floatSlider(self.volume_slider, q=True, value=True)
        cmds.floatField(self.extra_field, e=True, value=float_intensity)
        cmds.floatField(self.volume_field, e=True, value=volume_intensity)

    def update_float_slider(self, *args):
        field_intensity = cmds.floatField(self.extra_field, q=True, value=True)
        volume_intensity = cmds.floatField(self.volume_field, q=True, value=True)
        cmds.floatSlider(self.extra_slider, e=True, value=field_intensity)
        cmds.floatSlider(self.volume_slider, e=True, value=volume_intensity)

    def match_volume(self, *args):
        radius = cmds.artUserPaintCtx("ngSkinToolsLayerPaintCtx", q=True, radius=True)
        cmds.floatField(self.volume_field, e=True, value=radius)
        cmds.floatSlider(self.volume_slider, e=True, value=radius)

    def insert_menu(self):
        """ adds the equalizer tool to the ngSkin Tools menu bar """
        if cmds.menuItem('equalizer_item', exists=True):
            cmds.deleteUI('equalizer_item', menuItem=True)
            cmds.deleteUI('divider_item', menuItem=True)
        self.dividerEQ = cmds.menuItem(
            'divider_item',
            parent=self.ng_menu[-1],
            divider=True
        )
        self.editMenuEQ = cmds.menuItem(
            'equalizer_item',
            parent=self.ng_menu[-1],
            label=self.editMenuEQ,
            command=eq.open_equalizer
        )

    def insert_ui(self):
        """ adds the custom brush modes to an existing ngSkinTools UI """
        if cmds.frameLayout("extra_brushes", exists=True):
            cmds.deleteUI("extra_brushes")
        parent_layout = get_target_control(self.ui_paths["paint_tab"])
        self.extra_frame = cmds.frameLayout(
            "extra_brushes",
            label=self.extra_frame,
            collapsable=True,
            parent=parent_layout[0]
        )
        cmds.columnLayout(adjustableColumn=True)
        cmds.separator(style='none', height=5)
        cmds.rowLayout(
            numberOfColumns=1,
            adjustableColumn=1,
            columnAlign=(1, 'right'),
        )
        self.extra_check = cmds.checkBox(
            label=self.extra_check,
            value=False,
            onCommand=self.paint_tool_setup,
            offCommand=self.exit
        )
        cmds.setParent('..')
        self.radio_form = cmds.formLayout(numberOfDivisions=100)
        column = cmds.columnLayout(adjustableColumn=True)
        cmds.text(label=self.radio_text)
        cmds.setParent('..')
        mode_row = cmds.rowColumnLayout(numberOfColumns=2, columnWidth=[(1, 100), (2, 100)])
        self.mode_collection = cmds.radioCollection()
        cmds.radioButton("retract_radio", label=self.retract, onCommand=self.paint_mode, select=True)
        cmds.radioButton("spread_radio", label=self.spread, onCommand=self.paint_mode)
        cmds.radioButton("contrast_radio", label=self.contrast, onCommand=self.paint_mode)
        cmds.radioButton("gain_radio", label=self.gain, onCommand=self.paint_mode)
        cmds.radioButton("volume_radio", label=self.volume, onCommand=self.paint_mode)
        cmds.formLayout(
            self.radio_form,
            edit=True,
            enable=False,
            attachForm=[
                (column, 'top', 15),
                (column, 'left', 85),
                (mode_row, 'top', 5),
                (mode_row, 'left', 125),
            ]
        )
        cmds.setParent('..')
        cmds.setParent('..')
        self.intensity_row = cmds.rowLayout(
            numberOfColumns=3,
            adjustableColumn=3,
            columnAlign=(1, 'right'),
            columnWidth=[(1, 118), (2, 80), (3, 100)],
            columnOffset3=(0, 5, 0),
            columnAttach3=('both', 'left', 'left'),
            enable=False
        )
        cmds.text(label=self.intensity_label)
        self.extra_field = cmds.floatField()
        self.extra_slider = cmds.floatSlider()
        cmds.floatField(
            self.extra_field,
            e=True,
            width=80,
            minValue=0,
            maxValue=1,
            step=0.001,
            value=1,
            changeCommand=self.update_float_slider
        )
        cmds.floatSlider(
            self.extra_slider,
            e=True,
            minValue=0,
            maxValue=1,
            step=0.001,
            value=1,
            dragCommand=self.update_float_field,
            changeCommand=self.intensity
        )
        cmds.setParent('..')
        self.volume_row = cmds.rowLayout(
            numberOfColumns=4,
            adjustableColumn=4,
            columnAlign=(2, 'right'),
            columnWidth=[(1, 75), (2, 41), (3, 80), (4, 100)],
            columnOffset4=(4, 0, 5, 0),
            columnAttach4=('both', 'both', 'left', 'left'),
            enable=False
        )
        self.matchButton = cmds.button(
            label=self.matchButton,
            width=60,
            align='left',
            command=self.match_volume,
        )
        cmds.text(label=self.volume_label)
        self.volume_field = cmds.floatField(self.volume_field)
        self.volume_slider = cmds.floatSlider(self.volume_slider)
        cmds.floatField(
            self.volume_field,
            width=80,
            minValue=0,
            step=0.001,
            value=1,
            e=True,
            changeCommand=self.update_float_slider
        )
        cmds.floatSlider(
            self.volume_slider,
            minValue=0,
            step=0.001,
            value=1,
            e=True,
            dragCommand=self.update_float_field,
        )
        cmds.setParent('..')
        self.button_form = cmds.formLayout(numberOfDivisions=100)
        self.shrinkButton = cmds.button(
            label=self.shrinkButton,
            width=155,
            align='left',
            command=self.shrink
        )
        self.growButton = cmds.button(
            label=self.growButton,
            width=155,
            align='right',
            command=self.grow
        )
        self.floodButton = cmds.button(
            label=self.floodButton,
            width=315,
            command=self.flood,
            enable=False
        )
        cmds.formLayout(
            self.button_form,
            edit=True,
            enable=True,
            attachForm=[
                (self.shrinkButton, 'top', 35),
                (self.shrinkButton, 'left', 5),
                (self.growButton, 'top', 35),
                (self.growButton, 'left', 165),
                (self.floodButton, 'top', 5),
                (self.floodButton, 'left', 5),
            ]
        )
        cmds.setParent('..')
        mel.eval('source "ngSkinAlexUtilPaint.mel"')
        """
        self.brush_display_check = cmds.checkBox(
            label=self.brush_display_check,
            parent=
        )
        """

    def exit(self, *args):
        """ exits tool and resets it to the ngSkinTools settings """
        init_mel = Utils.createMelProcedure(ngLayerPaintCtxInitialize, [('string', 'mesh')], returnType='string')
        cmds.artUserPaintCtx(
            "ngSkinToolsLayerPaintCtx",
            e=True,
            setValueCommand="ngLayerPaintCtxSetValue",
            initializeCmd=init_mel,
            finalizeCmd="ngLayerPaintCtxFinalize",
            value=self.defaultVal
        )
        cmds.rowColumnLayout(self.ng_radio_layout[0], e=True, enable=True)
        cmds.checkBox(self.ng_checkboxes[0], e=True, enable=True)
        cmds.checkBox(self.ng_checkboxes[1], e=True, enable=True)
        cmds.rowLayout(self.ng_slider_rows[0], e=True, enable=True)
        cmds.formLayout(self.radio_form, e=True, enable=False)
        cmds.button(self.floodButton, e=True, enable=False)
        cmds.rowLayout(self.intensity_row, e=True, enable=False)
        cmds.rowLayout(self.volume_row, e=True, enable=False)
        ng_paint_mode = [
            (self.ng_radio_buttons.index(i) + 1)
            for i in self.ng_radio_buttons
            if cmds.radioButton(i, q=True, select=True) is True
        ]
        ng_intensity_value = cmds.floatSlider(self.ng_intensity[0], q=True, value=True)
        cmds.ngSkinLayer(paintOperation=ng_paint_mode[0], paintIntensity=ng_intensity_value)


def insert_ui_frame(*args):
    PE = PaintExtras()
    PE.insert_ui()
    PE.insert_menu()


def delete_ui_frame(*args):
    cmds.deleteUI('equalizer_item', menuItem=True)
    cmds.deleteUI('divider_item', menuItem=True)
    cmds.deleteUI("extra_brushes")
