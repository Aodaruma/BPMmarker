import re
from math import ceil, floor
from typing import List, Tuple
import bpy

bl_info = {
    "name": "animation: BPM marker",
    "author": "Aodaruma",
    "version": (3, 0),
    "blender": (3, 0, 0),
    "location": "",
    "description": "automatically detecting BPM and marking beats with BPM",
    "warning": "This is an alpha add-on! We will not be liable for any damages whatsoever resulting from the use of this add-on.",
    "support": "TESTING",
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
        self.layout.operator("aodaruma.librosa_installer",
                             text="Install librosa")

# ------------------------------------------------ #


class AODARUMA_OT_LibrosaInstaller(bpy.types.Operator):
    """
    Install librosa
    """
    bl_idname = "aodaruma.librosa_installer"
    bl_label = "Install librosa"
    bl_description = "Install librosa"
    bl_options = {'REGISTER'}

    def draw(self, context):
        layout = self.layout
        layout.label(
            text="Installing librosa will take a while. Please be patient.", icon='ERROR')

    def execute(self, context):
        try:
            import librosa
            self.report({'ERROR'}, "librosa is already installed")
            return {'CANCELLED'}
        except ImportError as e:
            if str(e).startswith("No module named"):
                if str(e).endswith("librosa"):
                    try:
                        import sys
                        import os
                        import subprocess
                        from subprocess import PIPE
                        from pathlib import Path

                        # specify the path of python binary of blender
                        python_bin_dir = Path(sys.exec_prefix) / "bin"
                        os_type = sys.platform
                        python_bin = None
                        for p in python_bin_dir.iterdir():
                            if "python" in p.name:
                                python_bin = p
                                break
                        if python_bin is None:
                            # raise Exception("Could not find python executable")
                            self.report(
                                {'ERROR'}, "Could not find python executable")
                            return {'ERROR'}

                        # try to install librosa using pip from subprocess (maybe some unexpected error occurs, idk)
                        proc = subprocess.run(
                            [python_bin, "-m", "pip", "install", "librosa"], stdout=PIPE, stderr=PIPE, text=True)  # type: ignore
                        print("-"*10, "\n", proc.stdout, "\n", "-"*10)
                        print("BPMmarker: librosa is installed.")
                        try:
                            import librosa
                            self.report(
                                {"INFO"}, "BPMmarker: Finally you can use librosa and all features of BPMmarker. Yay!")
                        except ImportError as e:
                            if str(e).startswith("No module named"):
                                if str(e).endswith("librosa"):
                                    self.report(
                                        {"WARNING"}, "BPMmarker: librosa was installed but maybe blender needs to restart. Try it!")
                                    # self.report(
                                    #     {'ERROR'}, "BPMmarker: Cannnot install librosa. Maybe something went wrong so report it to the developer.")
                                else:
                                    self.report(
                                        {'ERROR'}, f"BPMmarker: Unknown module ({e.name}) import error occurred. Report it to the developer.")
                                    return {'ERROR'}
                            else:
                                self.report(
                                    {'ERROR'}, f"BPMmarker: Unknown error occurred. Report it to the developer: {e}")
                            librosa = None
                            return {'ERROR'}
                    except Exception as e:
                        self.report(
                            {'ERROR'}, f"BPMmarker: Unknown error occurred. Report it to the developer: {e}")
                        librosa = None
                        return {'ERROR'}
                else:
                    self.report(
                        {'ERROR'}, "BPMmarker: Unknown module ({e.name}) import error occurred. Report it to the developer.")
                    librosa = None
                    return {'ERROR'}
            else:
                self.report(
                    {'ERROR'}, f"BPMmarker: Unknown error occurred. Report it to the developer: {e}")
                librosa = None
                return {'ERROR'}
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


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

        bpm: float = self.BPM
        beat: int = self.beat
        start: int = self.start
        end: int = self.end
        standard: bool = self.standard
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
                    c=counter+1, m="|" if counter == 0 else ""), round(frame+start))
            else:
                tms.new("{m}{c}{m}".format(
                    c=counter+1, m="|" if counter == 0 else ""), frame=round(frame+start))
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


class AODARUMA_OT_BPMmarkerAutomatically(bpy.types.Operator):
    bl_idname = "aodaruma.bpmmarker_automatically"
    bl_label = "BPM detector & marker"
    bl_description = "automatically detecting BPM using librosa and marking beats with BPM"
    bl_options = {'REGISTER', 'UNDO'}

#   def execute(self, context):
#     print("pushed")
#     return {'FINISHED'}
    beat: bpy.props.IntProperty(
        name="Beats", default=4, min=1, max=256, description="beats per measure")
    start: bpy.props.IntProperty(
        name="Start Frame", default=0, description="start frame of duration that marker will be added")
    end: bpy.props.IntProperty(
        name="End Frame", default=250, description="end frame of duration that marker will be added")
    # standard: bpy.props.IntProperty(name="Standard Frame", default=0)
    beat_shift: bpy.props.IntProperty(
        name="Beat Shift", default=0, min=-256, max=256, description="how many beats to shift")
    hop_length: bpy.props.IntProperty(
        name="Hop Length", default=512, min=1, description="number of audio samples between successive onset_envelope values (librosa)\nIf you feel the marker's position shifts incorrectly, increase this value such as 1024 (power of 2)")
    tightness: bpy.props.FloatProperty(
        name="Tightness", default=100, description="tightness of beat distribution around tempo (librosa)\nIf you feel the marker's position shifts incorrectly, increase this value.")
    isClearPreMark: bpy.props.BoolProperty(
        name="clear previous marks", default=True, description="whether to clear previous BPM markers")

    def execute(self, context: bpy.types.Context):
        if librosa is None:
            self.report(
                {"ERROR"}, 'librosa is not installed. please install librosa with pip (generally installed when blender installs this addon) and restart blender')
            return {'CANCELLED'}

        scene = context.scene
        beat = self.beat
        start = self.start
        end = self.end
        # standard = self.standard
        beat_shift = self.beat_shift
        hop_length = self.hop_length
        tightness = self.tightness
        fps = scene.render.fps
        tms = scene.timeline_markers

        selected_sequence = context.scene.sequence_editor.active_strip

        if selected_sequence is None:
            self.report({"ERROR"}, "No sequence selected")
            return {'ERROR'}
        if not isinstance(selected_sequence, bpy.types.SoundSequence):
            self.report({"ERROR"}, "Selected sequence is not a sound sequence")
            return {'ERROR'}

        sequence_start = selected_sequence.frame_start
        sequence_end = selected_sequence.frame_final_end

        if self.isClearPreMark:
            for m in tms:
                if re.match(r"\|?[\d]\|?", m.name):
                    tms.remove(m)

        # BPM detect using librosa
        wm = context.window_manager
        wm.progress_begin(0, 100)
        wm.progress_update(0)

        print("Analyzing...")
        y, sr = librosa.load(selected_sequence.sound.filepath, sr=None)
        tempo, beat_times = librosa.beat.beat_track(
            y=y, sr=sr, hop_length=hop_length, tightness=tightness, units="time")
        wm.progress_update(50)
        print("Analyzed the audio!;", "BPM:", tempo, ";")

        # Marking beats
        # fpb = 60 * fps / tempo
        # deltaframe = (standard-sequence_start) % fpb
        # frame = sequence_start+deltaframe
        # while frame <= sequence_end and frame <= end:
        #     counter = floor((frame - standard - deltaframe) / fpb) % beat
        #     if VERSION < (2, 80, 0):
        #         tms.new("{m}{c}{m}".format(
        #             c=counter+1, m="|" if counter == 0 else ""), frame)
        #     else:
        #         tms.new("{m}{c}{m}".format(
        #             c=counter+1, m="|" if counter == 0 else ""), frame=frame)
        #     frame += fpb

        # Marking beats with beat_frames
        beat_frames = map(lambda x: int(x*fps), beat_times)
        now_beats = beat_shift
        for frame in beat_frames:
            counter = now_beats % beat
            if (frame >= sequence_start and frame >= start) and (frame <= sequence_end and frame <= end):
                if VERSION < (2, 80, 0):
                    tms.new("{m}{c}{m}".format(
                        c=counter+1, m="|" if counter == 0 else ""), frame+sequence_start)
                else:
                    tms.new("{m}{c}{m}".format(
                        c=counter+1, m="|" if counter == 0 else ""), frame=frame+sequence_start)
            now_beats += 1
            wm.progress_update(
                50+int(50*(frame-sequence_start)/(sequence_end-sequence_start)))

        wm.progress_end()
        self.report({'INFO'}, f'Analyzed and Added markers! BPM: {tempo}')

        return{'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout

        # Required options
        layout.prop(self, "beat")
        row = layout.row()
        row.prop(self, "start")
        row.prop(self, "end")
        layout.prop(self, "standard")
        layout.prop(self, "beat_shift")

        # Advanced options
        box = layout.box()
        box.label(text="Advanced Options")
        box.prop(self, "hop_length")
        box.prop(self, "tightness")

        layout.prop(self, "isClearPreMark")
        layout.label(
            text="WARNING: analyzing audio will take some time!", icon='ERROR')


classes = [
    AODARUMA_OT_LibrosaInstaller,
    AODARUMA_OT_BPMmarkerManually,
    AODARUMA_OT_BPMmarkerAutomatically,
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
