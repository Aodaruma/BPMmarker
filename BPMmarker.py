import bpy

bl_info = {
    "name": "animation: BPM marker",
    "author": "Aodaruma",
    "version": (1, 0),
    "blender": (2, 80, 0),
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

class UI(bpy.types.Panel):
    bl_label = "BPM marker"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS" if bpy.app.version < (2,80,0) else "UI"
    bl_category = "Tools"
    def draw(self, context):
        self.layout.operator("aodaruma.bpmmarker", text="Mark")

# ------------------------------------------------ #

class MarkingButton(bpy.types.Operator):
    bl_idname = "aodaruma.bpmmarker"
    bl_label = "BPM marker"
  
#   def execute(self, context):
#     print("pushed")
#     return {'FINISHED'}
    BPM = bpy.props.IntProperty(name="BPM",default=120)
    beat = bpy.props.IntProperty(name="Beats",default=4)
    isClearPreMark = bpy.props.BoolProperty(name="clear previous marks",default=True)
    
    def execute(self, context):
        scene = bpy.context.scene

        bpm = self.BPM
        beat = self.beat
        fps = scene.render.fps

        if self.isClearPreMark:
            scene.timeline_markers.clear()

        fpb = 60 * fps / bpm
        print("frames per beat", fpb)
        frame = scene.frame_start
        while frame < scene.frame_end:
            counter = round(frame / fpb % beat) + 1
            if VERSION < (2,80,0):
                scene.timeline_markers.new("{m}{c}{m}".format(c=counter, m="|" if counter == 1 else ""), frame)
            else:
                scene.timeline_markers.new("{m}{c}{m}".format(c=counter, m="|" if counter == 1 else ""), frame=frame)
            frame += fpb

        return{'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    
classes = (
    UI,
    MarkingButton,
)

for cls in classes:
  bpy.utils.register_class(cls)

####################################

def register():
    print(bl_info["name"]+" registered.")

def unregister():
    print(bl_info["name"]+" unregistered.")

if __name__ == "__main__":
    register()
    
####################################
    
# print("done!")