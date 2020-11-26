import maya.cmds as cmds
import alex_utils as utils
from ngSkinTools.mllInterface import MllInterface


class Equalize(object):
    def __init__(self):
        self.mll = MllInterface()
        self.ngs_vert_count = -1
        self.ngs_layer_id = -1
        self.intensity = -1
        self.ngs_influence = None
        self.vert_weight_dict = {}
        self.vert_weight_list = []
        self.ngs_weight_dict = {}
        self.ngs_weight_list = []
        self.new_weight_list = []
        self.selection_vert = []
        self.vertex_list = []
        self.id_list = []

        self.modes = {
            "max": self.vert_max,
            "min": self.vert_min,
            "avg": self.vert_avg,
            "first": self.vert_first,
            "last": self.vert_last
        }

    def get_data(self, check):
        self.ngs_weight_dict = {}
        self.vert_weight_dict = {}
        self.selection_vert = cmds.ls(os=True)
        if not self.selection_vert:
            return False
        if not check:
            self.ngs_influence = [("selected influence:", self.mll.getCurrentPaintTarget())]
        else:
            self.ngs_influence = self.mll.listLayerInfluences(layerId=None, activeInfluences=True)
        self.mll = MllInterface()
        self.ngs_layer_id = self.mll.getCurrentLayer()
        self.ngs_vert_count = self.mll.getVertCount()
        self.vertex_list = cmds.ls(self.selection_vert, flatten=True)
        self.id_list = list(map(lambda x: x[x.find("[") + 1:x.find("]")], self.vertex_list))
        for influences in self.ngs_influence:
            influence_weights = self.mll.getInfluenceWeights(self.ngs_layer_id, influences[1])
            vert_weights = [influence_weights[int(i)] for i in self.id_list]
            self.ngs_weight_dict[influences] = influence_weights
            self.vert_weight_dict[influences] = vert_weights
        return True

    def set_vert(self, mode, intensity):
        self.intensity = intensity
        for influences in self.ngs_influence:
            self.new_weight_list = []
            self.ngs_weight_list = self.ngs_weight_dict[influences]
            self.vert_weight_list = self.vert_weight_dict[influences]
            self.modes[mode]()
            self.mll.setInfluenceWeights(self.ngs_layer_id, influences[1], self.new_weight_list)

    def vert_max(self):
        for i in range(self.ngs_vert_count):
            vertex_weight = self.ngs_weight_list[i]
            if str(i) not in self.id_list or vertex_weight == max(self.vert_weight_list):
                self.new_weight_list.append(vertex_weight)
                continue
            new_weight = vertex_weight + ((max(self.vert_weight_list) - vertex_weight) * self.intensity)
            self.new_weight_list.append(new_weight)

    def vert_min(self):
        for i in range(self.ngs_vert_count):
            vertex_weight = self.ngs_weight_list[i]
            if str(i) not in self.id_list or vertex_weight == min(self.vert_weight_list):
                self.new_weight_list.append(vertex_weight)
                continue
            new_weight = vertex_weight - ((vertex_weight - min(self.vert_weight_list)) * self.intensity)
            self.new_weight_list.append(new_weight)

    def vert_avg(self):
        average = sum(self.vert_weight_list) / float(len(self.vert_weight_list))
        for i in range(self.ngs_vert_count):
            vertex_weight = self.ngs_weight_list[i]
            if str(i) not in self.id_list or vertex_weight == average:
                self.new_weight_list.append(vertex_weight)
                continue
            new_weight = vertex_weight - ((vertex_weight - average) * self.intensity)
            self.new_weight_list.append(new_weight)

    def vert_first(self):
        first = self.vert_weight_list[0]
        for i in range(self.ngs_vert_count):
            vertex_weight = self.ngs_weight_list[i]
            if str(i) not in self.id_list or vertex_weight == first:
                self.new_weight_list.append(vertex_weight)
                continue
            new_weight = vertex_weight - ((vertex_weight - first) * self.intensity)
            self.new_weight_list.append(new_weight)

    def vert_last(self):
        last = self.vert_weight_list[-1]
        for i in range(self.ngs_vert_count):
            vertex_weight = self.ngs_weight_list[i]
            if str(i) not in self.id_list or vertex_weight == last:
                self.new_weight_list.append(vertex_weight)
                continue
            new_weight = vertex_weight - ((vertex_weight - last) * self.intensity)
            self.new_weight_list.append(new_weight)


class Comparison_UI(object):
    def __init__(self):
        self.window = "equalizer_ui"
        self.title = "ng Vertex Equalizer"
        self.size = (300, 125)
        self.eq = Equalize()

        self.last_call = ""
        self.green = utils.rgb_to_float(120, 220, 120)
        self.red = utils.rgb_to_float(220, 120, 120)

        self.max_button = "Max +"
        self.min_button = "Min -"
        self.avg_button = "Avg ="
        self.first_button = "To First"
        self.last_button = "To Last"
        self.scroll_button = "To List Selection"
        self.all_check = "Affect All Influences:"

        self.slider = "intensity_slider"
        self.field = "intensity_field"
        self.columnForm = "column_form"
        self.buttonForm = "button_form"
        self.intensityForm = "intensity_form"

    def button_color(self, *args):
        cmds.button(self.max_button, e=True, backgroundColor=(.361, .361, .361))
        cmds.button(self.min_button, e=True, backgroundColor=(.361, .361, .361))
        cmds.button(self.avg_button, e=True, backgroundColor=(.361, .361, .361))
        cmds.button(self.first_button, e=True, backgroundColor=(.361, .361, .361))
        cmds.button(self.last_button, e=True, backgroundColor=(.361, .361, .361))

    def do_first(self, *args):
        all_check = cmds.checkBox(self.all_check, q=True, value=True)
        if not self.eq.get_data(all_check):
            return
        intensity = cmds.floatSlider(self.slider, q=True, value=True)
        self.eq.set_vert("first", intensity)
        self.last_call = "first"
        self.button_color()
        cmds.button(self.first_button, e=True, backgroundColor=(self.green[0], self.green[1], self.green[2]))

    def do_last(self, *args):
        all_check = cmds.checkBox(self.all_check, q=True, value=True)
        if not self.eq.get_data(all_check):
            return
        intensity = cmds.floatSlider(self.slider, q=True, value=True)
        self.eq.set_vert("last", intensity)
        self.last_call = "last"
        self.button_color()
        cmds.button(self.last_button, e=True, backgroundColor=(self.green[0], self.green[1], self.green[2]))

    def do_max(self, *args):
        all_check = cmds.checkBox(self.all_check, q=True, value=True)
        if not self.eq.get_data(all_check):
            return
        intensity = cmds.floatSlider(self.slider, q=True, value=True)
        self.eq.set_vert("max", intensity)
        self.last_call = "max"
        self.button_color()
        cmds.button(self.max_button, e=True, backgroundColor=(self.green[0], self.green[1], self.green[2]))

    def do_min(self, *args):
        all_check = cmds.checkBox(self.all_check, q=True, value=True)
        if not self.eq.get_data(all_check):
            return
        intensity = cmds.floatSlider(self.slider, q=True, value=True)
        self.eq.set_vert("min", intensity)
        self.last_call = "min"
        self.button_color()
        cmds.button(self.min_button, e=True, backgroundColor=(self.green[0], self.green[1], self.green[2]))

    def do_avg(self, *args):
        all_check = cmds.checkBox(self.all_check, q=True, value=True)
        if not self.eq.get_data(all_check):
            return
        intensity = cmds.floatSlider(self.slider, q=True, value=True)
        self.eq.set_vert("avg", intensity)
        self.last_call = "avg"
        self.button_color()
        cmds.button(self.avg_button, e=True, backgroundColor=(self.green[0], self.green[1], self.green[2]))

    def do_drag(self, *args):
        self.update_float_field()
        selection_vert = cmds.ls(selection=True)
        if not selection_vert:
            return
        intensity = cmds.floatSlider(self.slider, q=True, value=True)
        if self.last_call == "max":
            self.eq.set_vert("max", intensity)
        if self.last_call == "min":
            self.eq.set_vert("min", intensity)
        if self.last_call == "avg":
            self.eq.set_vert("avg", intensity)
        if self.last_call == "first":
            self.eq.set_vert("first", intensity)
        if self.last_call == "last":
            self.eq.set_vert("last", intensity)

    def update_float_field(self, *args):
        float_intensity = cmds.floatSlider(self.slider, q=True, value=True)
        cmds.floatField(self.field, e=True, value=float_intensity)

    def update_float_slider(self, *args):
        field_intensity = cmds.floatField(self.field, q=True, value=True)
        cmds.floatSlider(self.slider, e=True, value=field_intensity)

    def create(self):
        if cmds.window(self.window, exists=True):
            cmds.deleteUI(self.window, window=True)
        self.window = cmds.window(
            self.window,
            title=self.title,
            widthHeight=self.size
        )
        cmds.columnLayout(adjustableColumn=True)
        cmds.rowColumnLayout(numberOfColumns=3, columnWidth=[(1, 100), (2, 100), (3, 100)])
        self.min_button = cmds.button(label=self.min_button, command=self.do_min, enableBackground=True)
        self.avg_button = cmds.button(label=self.avg_button, command=self.do_avg, enableBackground=True)
        self.max_button = cmds.button(label=self.max_button, command=self.do_max, enableBackground=True)
        cmds.setParent('..')
        cmds.separator(style='none', height=5)
        cmds.rowColumnLayout(numberOfColumns=2, columnWidth=[(1, 150), (2, 150), ])
        self.first_button = cmds.button(label=self.first_button, command=self.do_first, enableBackground=True)
        self.last_button = cmds.button(label=self.last_button, command=self.do_last, enableBackground=True)
        cmds.setParent('..')
        cmds.separator(style='none', height=5)
        cmds.rowLayout(
            numberOfColumns=3,
            adjustableColumn=3,
            columnAlign=(1, 'right'),
            columnWidth=[(1, 60), (2, 80), (3, 160)],
            columnOffset3=(0, 5, 0),
            columnAttach3=('both', 'left', 'left'),
        )
        cmds.text(label='Intensity:')
        self.field = cmds.floatField()
        self.slider = cmds.floatSlider()
        cmds.floatField(
            self.field,
            e=True,
            width=80,
            minValue=0,
            maxValue=1,
            step=0.001,
            value=1,
            dragCommand=self.do_drag,
            changeCommand=self.update_float_slider
        )
        cmds.floatSlider(
            self.slider,
            e=True,
            minValue=0,
            maxValue=1,
            step=0.001,
            value=1,
            dragCommand=self.do_drag,
        )
        cmds.setParent('..')
        cmds.rowLayout(
            numberOfColumns=1,
            adjustableColumn=1,
            columnAlign=(1, 'left'),
            columnOffset1=25
        )
        self.all_check = cmds.checkBox(
            label=self.all_check,
            value=True,
        )
        cmds.setParent('..')
        cmds.setParent('..')
        cmds.showWindow()
        self.button_color()


def open_equalizer(*args):
    """ opens the Equalizer UI window """
    create_eq = Comparison_UI()
    create_eq.create()
