# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
    "name": "Import LightWave Objects",
    "author": "Dave Keeshan, Ken Nign (Ken9) and Gert De Roost",
    "version": (1, 4, 6),
    "blender": (2, 81, 16),
    "location": "File > Import > LightWave Object (.lwo)",
    "description": "Imports a LWO file including any UV, Morph and Color maps. "
    "Can convert Skelegons to an Armature.",
    "warning": "",
    "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.6/Py/"
    "Scripts/Import-Export/LightWave_Object",
    "category": "Import-Export",
}

# Copyright (c) Ken Nign 2010
# ken@virginpi.com
#
# Version 1.3 - Aug 11, 2011
#
# Loads a LightWave .lwo object file, including the vertex maps such as
# UV, Morph, Color and Weight maps.
#
# Will optionally create an Armature from an embedded Skelegon rig.
#
# Point orders are maintained so that .mdds can exchanged with other
# 3D programs.
#
#
# Notes:
# NGons, polygons with more than 4 points are supported, but are
# added (as triangles) after the vertex maps have been applied. Thus they
# won't contain all the vertex data that the original ngon had.
#
# Blender is limited to only 8 UV Texture and 8 Vertex Color maps,
# thus only the first 8 of each can be imported.
#
# History:
#
# 1.3 Fixed CC Edge Weight loading.
#
# 1.2 Added Absolute Morph and CC Edge Weight support.
#     Made edge creation safer.
# 1.0 First Release

import os
import bpy

from .lwoObject import lwoObject, lwoNoImageFoundException, lwoUnsupportedFileException
from .construct_mesh import build_objects


class _choices:
    __slots__ = (
        "add_subd_mod",
        "load_hidden",
        "skel_to_arm",
        "use_existing_materials",
        "search_paths",
        "cancel_search",
        "images",
        "recursive",
    )

    def __init__(
        self,
        ADD_SUBD_MOD=True,
        LOAD_HIDDEN=False,
        SKEL_TO_ARM=True,
        USE_EXISTING_MATERIALS=False,
    ):
        self.add_subd_mod = ADD_SUBD_MOD
        self.load_hidden = LOAD_HIDDEN
        self.skel_to_arm = SKEL_TO_ARM
        self.use_existing_materials = USE_EXISTING_MATERIALS
        self.search_paths = []
        self.cancel_search = False
        self.images = {}
        self.recursive = True


from bpy.props import StringProperty, BoolProperty


class MESSAGE_OT_Box(bpy.types.Operator):
    bl_idname = "message.messagebox"
    bl_label = ""


    message: bpy.props.StringProperty(
        name="message", description="message", default="",
    )
    ob: bpy.props.BoolProperty(name="ob", description="ob", default=False,)







    def invoke(self, context, event):  # gui: no cover
        return context.window_manager.invoke_props_dialog(self, width=400)

    def execute(self, context):  # gui: no cover
        # self.report({'ERROR'}, self.message)
        self.report({"INFO"}, self.message)
        print(self.message)
        if self.ob:
            bpy.ops.open.browser("INVOKE_DEFAULT")
        return {"FINISHED"}

    def draw(self, context):  # gui: no cover
        self.layout.label(text=self.message)
        self.layout.label(text="")


class OPEN_OT_browser(bpy.types.Operator):
    bl_idname = "open.browser"
    bl_label = "Select Image Search Path"
    bl_options = {"REGISTER", "UNDO"}


    directory: StringProperty(subtype="DIR_PATH")
    recursive: BoolProperty(
        name="Recursive Search",
        description="Uncheck to disable recursive search",
        default=True,
    )
    cancel_search: BoolProperty(
        name="Cancel Search",
        description="If no further images are to be found",
        default=False,
    )














    def invoke(self, context, event):  # gui: no cover
        wm = context.window_manager
        wm.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):  # gui: no cover
        lwo = bpy.types.Scene.lwo
        ch = bpy.types.Scene.ch

        ch.search_paths.append(self.directory)
        ch.cancel_search = self.cancel_search
        ch.recursive = self.recursive
        try:
            lwo.resolve_clips()
            lwo.validate_lwo()
            build_objects(lwo, ch)
        except lwoNoImageFoundException as msg:
            bpy.ops.message.messagebox("INVOKE_DEFAULT", message=str(msg), ob=True)

        del lwo
        return {"FINISHED"}


class IMPORT_OT_lwo(bpy.types.Operator):
    """Import LWO Operator"""

    bl_idname = "import_scene.lwo"
    bl_label = "Import LWO"
    bl_description = "Import a LightWave Object file"
    bl_options = {"REGISTER", "UNDO"}

    bpy.types.Scene.ch = None
    bpy.types.Scene.lwo = None


    filepath: StringProperty(
        name="File Path",
        description="Filepath used for importing the LWO file",
        maxlen=1024,
        default="",
    )

    ADD_SUBD_MOD: BoolProperty(
        name="Apply SubD Modifier",
        description="Apply the Subdivision Surface modifier to layers with Subpatches",
        default=True,
    )
    LOAD_HIDDEN: BoolProperty(
        name="Load Hidden Layers",
        description="Load object layers that have been marked as hidden",
        default=False,
    )
    SKEL_TO_ARM: BoolProperty(
        name="Create Armature",
        description="Create an armature from an embedded Skelegon rig",
        default=True,
    )
    USE_EXISTING_MATERIALS: BoolProperty(
        name="Use Existing Materials",
        description="Use existing materials if a material by that name already exists",
        default=False,
    )






























    def invoke(self, context, event):  # gui: no cover
        wm = context.window_manager
        wm.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):

        ch = bpy.types.Scene.ch
        ch.add_subd_mod = self.ADD_SUBD_MOD
        ch.load_hidden = self.LOAD_HIDDEN
        ch.skel_to_arm = self.SKEL_TO_ARM
        ch.use_existing_materials = self.USE_EXISTING_MATERIALS
        #ch.search_paths = []
        ch.images = {}
        # ch.cancel_search          = False


#         import cProfile
#         import pstats
#         profiler = cProfile.Profile()
#         profiler.enable()

        lwo = lwoObject(self.filepath)
        bpy.types.Scene.lwo = lwo

        try:
            lwo.read(ch)
        except lwoUnsupportedFileException as err:
            if bpy.app.background:
                raise err
            else:
                bpy.ops.message.messagebox(
                    "INVOKE_DEFAULT", message=str(err)
                )  # gui: no cover

        try:
            lwo.resolve_clips()
            lwo.validate_lwo()
            build_objects(lwo, ch)
        except lwoNoImageFoundException as err:
            if bpy.app.background:
                raise err
            else:
                bpy.ops.message.messagebox(
                    "INVOKE_DEFAULT", message=str(err), ob=True
                )  # gui: no cover
#         profiler.disable()
#         #profiler.print_stats()
#         p = pstats.Stats(profiler)
#         p.sort_stats('time').print_stats()

        del lwo
        # With the data gathered, build the object(s).
        return {"FINISHED"}


def menu_func(self, context):  # gui: no cover
    self.layout.operator(IMPORT_OT_lwo.bl_idname, text="LightWave Object (.lwo)")


# Panel
class IMPORT_PT_Debug(bpy.types.Panel):
    bl_idname = "IMPORT_PT_Debug"

    # region = "UI"
    region = "WINDOW"
    # region = "TOOLS"
    space = "PROPERTIES"




    bl_label = "DEBUG"
    bl_space_type = space
    bl_region_type = region
    bl_category = "Tools"

    def draw(self, context):  # gui: no cover
        layout = self.layout

        col = layout.column(align=True)
        col.operator("import_scene.lwo", text="Import LWO")
        col.operator("open.browser", text="File Browser")


classes = (
    IMPORT_OT_lwo,
    OPEN_OT_browser,
    MESSAGE_OT_Box,
)

def register():

    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.TOPBAR_MT_file_import.append(menu_func)




    ch = _choices()
    bpy.types.Scene.ch = ch


def unregister():  # pragma: no cover

    for cls in classes:
        bpy.utils.unregister_class(cls)

    bpy.types.TOPBAR_MT_file_import.remove(menu_func)




    del bpy.types.Scene.ch

if __name__ == "__main__":  # pragma: no cover
    register()
