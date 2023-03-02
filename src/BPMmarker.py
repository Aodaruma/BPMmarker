import re
from math import ceil, floor
from typing import List
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

VERSION = bpy.app.version


class BPMmarker_DopesheetPanel(bpy.types.Panel):
    bl_label = "BPM marker"
    bl_space_type = "DOPESHEET_EDITOR"
    bl_region_type = "TOOLS" if bpy.app.version < (2, 80, 0) else "UI"
    bl_category = "BPM marker"

    def draw(self, context):
        self.layout.operator("aodaruma.bpmmarker", text="Run to Mark")


class BPMmarker_GrapheditorPanel(bpy.types.Panel):
    bl_label = "BPM marker"
    bl_space_type = "GRAPH_EDITOR"
    bl_region_type = "TOOLS" if bpy.app.version < (2, 80, 0) else "UI"
    bl_category = "BPM marker"

    def draw(self, context):
        self.layout.operator("aodaruma.bpmmarker", text="Run to Mark")

# ------------------------------------------------ #


class AODARUMA_OT_BPMmaker(bpy.types.Operator):
    bl_idname = "aodaruma.bpmmarker"
    bl_label = "BPM marker"
    bl_description = "automatically marking beats with BPM"
    bl_options = {'REGISTER', 'UNDO'}

#   def execute(self, context):
#     print("pushed")
#     return {'FINISHED'}
    BPM: bpy.props.IntProperty(name="BPM", default=120, min=1)
    beat: bpy.props.IntProperty(name="Beats", default=4, min=1, max=256)
    start: bpy.props.IntProperty(name="BeginFrame", default=0)
    end: bpy.props.IntProperty(
        name="EndFrame", default=250)
    isClearPreMark: bpy.props.BoolProperty(
        name="clear previous marks", default=True)

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
        frame = 0
        while frame < end-start:
            counter = floor((frame / fpb) % beat)
            if VERSION < (2, 80, 0):
                tms.new("{m}{c}{m}".format(
                    c=counter+1, m="|" if counter == 0 else ""), frame+start)
            else:
                tms.new("{m}{c}{m}".format(
                    c=counter+1, m="|" if counter == 0 else ""), frame=int(frame+start))
            frame += fpb

        return{'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


classes = [
    AODARUMA_OT_BPMmaker,
    BPMmarker_DopesheetPanel,
    BPMmarker_GrapheditorPanel
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
