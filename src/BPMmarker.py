import re
from math import ceil, floor
from typing import List, Tuple
import bpy

bl_info = {
    "name": "animation: BPM marker",
    "author": "Aodaruma",
    "version": (2, 0),
    "blender": (3, 0, 0),
    "location": "",
    "description": "automatically marking beats with BPM",
    "warning": "",
    "support": "COMMUNITY",
    "wiki_url": "https://github.com/Aodaruma/BPMmark_maker",
    "tracker_url": "",
    "category": "Animation"
}
####################################

VERSION: Tuple[int, int, int] = bpy.app.version


class AODARUMA_PT_BPMmarker_DopesheetPanel(bpy.types.Panel):
    bl_label = "BPM marker"
    bl_space_type = "DOPESHEET_EDITOR"
    bl_region_type = "TOOLS" if VERSION < (2, 80, 0) else "UI"
    bl_category = "BPM marker"

    def draw(self, context):

        self.layout.operator("aodaruma.bpmmarker_manually",
                             text="Mark manually")


class AODARUMA_PT_BPMmarker_GrapheditorPanel(bpy.types.Panel):
    bl_label = "BPM marker"
    bl_space_type = "GRAPH_EDITOR"
    bl_region_type = "TOOLS" if VERSION < (2, 80, 0) else "UI"
    bl_category = "BPM marker"

    def draw(self, context):
        self.layout.operator("aodaruma.bpmmarker_manually",
                             text="Mark manually")


class AODARUMA_PT_BPMmarker_SequencerPanel(bpy.types.Panel):
    bl_label = "BPM marker"
    bl_space_type = "SEQUENCE_EDITOR"
    bl_region_type = "TOOLS" if VERSION < (2, 80, 0) else "UI"
    bl_category = "BPM marker"

    def draw(self, context):
        self.layout.operator("aodaruma.bpmmarker_manually",
                             text="Mark manually")
        self.layout.operator("aodaruma.bpmmarker_automatically",
                             text="Auto BPM detect and Add marker")

# ------------------------------------------------ #


class AODARUMA_OT_BPMmarkerManually(bpy.types.Operator):
    bl_idname = "aodaruma.bpmmarker_manually"
    bl_label = "BPM marker"
    bl_description = "automatically marking beats with BPM"
    bl_options = {'REGISTER', 'UNDO'}

#   def execute(self, context):
#     print("pushed")
#     return {'FINISHED'}
    BPM: bpy.props.FloatProperty(
        name="BPM", default=120, min=1, description="BPM")
    beat: bpy.props.IntProperty(
        name="Beats", default=4, min=1, max=256, description="The number of beats")
    start: bpy.props.IntProperty(
        name="Start Frame", default=0, description="Start frame that markers will be added")
    end: bpy.props.IntProperty(
        name="End Frame", default=250, description="End frame that markers will be added")
    isStandardSameAsBegin: bpy.props.BoolProperty(
        name="set standard frame to same as begin", default=True, description="The reference frame for counting BPM beats is the same as the start frame.")
    standard: bpy.props.IntProperty(
        name="Standard Frame", default=0, description="The reference frame for counting BPM beats")
    isClearPreMark: bpy.props.BoolProperty(
        name="clear previous marks", default=True, description="Clear previous BPM markers")

    def execute(self, context: bpy.types.Context):
        scene = context.scene

        bpm = self.BPM
        beat = self.beat
        start = self.start
        end = self.end
        fps = scene.render.fps
        tms = scene.timeline_markers

        if self.isClearPreMark:
            for m in tms:
                if re.match(r"\|?[\d]\|?", m.name):
                    tms.remove(m)

        fpb = 60 * fps / bpm
        # print(fps, bpm)
        print("frames per beat", fpb)
        # frame = scene.frame_start
        frame = start
        if self.isStandardSameAsBegin:
            now_beat = 0
        else:
            now_beat = floor((start - standard) / fpb)
        while frame <= end:
            counter = now_beat % beat
            if VERSION < (2, 80, 0):
                tms.new("{m}{c}{m}".format(
                    c=counter+1, m="|" if counter == 0 else ""), frame+start)
            else:
                tms.new("{m}{c}{m}".format(
                    c=counter+1, m="|" if counter == 0 else ""), frame=frame+start)
            frame += fpb
            now_beat += 1

        return{'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "BPM")
        layout.prop(self, "beat")
        col = layout.column()
        row1 = col.row()
        row1.prop(self, "start")
        row1.prop(self, "end")
        col.prop(self, "isStandardSameAsBegin")
        row2 = col.row()
        row2.prop(self, "standard")
        row2.enabled = not self.isStandardSameAsBegin
        layout.prop(self, "isClearPreMark")

classes = [
    AODARUMA_OT_BPMmarkerManually,
    AODARUMA_PT_BPMmarker_DopesheetPanel,
    AODARUMA_PT_BPMmarker_GrapheditorPanel,
    AODARUMA_PT_BPMmarker_SequencerPanel
]

####################################


def register():
    for c in classes:
        bpy.utils.register_class(c)
    # bpy.types.VIEW3D_MT_object.append(UI)
    print(bl_info["name"]+" registered.")


def unregister():
    # bpy.types.VIEW3D_MT_object.remove(UI)
    for c in classes:
        bpy.utils.unregister_class(c)
    print(bl_info["name"]+" unregistered.")


if __name__ == "__main__":
    register()

####################################

# print("done!")
