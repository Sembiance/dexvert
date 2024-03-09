
'''
hypov8
==========
impliment md3 importer to suit kingpin conversion
backward compatable

based on https://github.com/laurirasanen/blender-md3

change log:
===========
v0.4.4.1
- removed creating new scene for import. moved to collections (2.8)
- added node setup for skin
- added assemble of mesh to tags (option)
- blender 2.79 support (importer only done)
- multiple selection import implemented


todo:
=====
- exporter. backward compatable
- read .skin file
'''


bl_info = {
    "name": "Quake 3 Model (.md3)-hy-",
    "author": "hypov8 & Contributors",
    "version": (0, 4, 4, 1),
    "blender": (2, 80, 0),
    "location": "File > Import-Export > Quake 3 Model",
    "description": "Quake 3 Model format (.md3)",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "https://github.com/hypov8/blender-md3_2.7-3.2/issues",
    "category": "Import-Export",
}


import bpy
import struct
from bpy.props import (
    StringProperty,
    BoolProperty,
    CollectionProperty
)
from bpy_extras.io_utils import ImportHelper, ExportHelper

from .utils import (  # backward compatable
    make_annotations,
    get_menu_export,
    get_menu_import,
    set_select_state
)


if bpy.app.version < (2, 80):  # remove nag
    bl_info["blender"] = (2, 79, 0)


class ImportMD3_KP(bpy.types.Operator, ImportHelper):
    '''Import a Quake 3 Model MD3 file'''
    bl_idname = "import_scene.md3"
    bl_label = 'Import MD3'
    filename_ext = ".md3"

    # filters
    filter_glob = StringProperty(default="*.md3", options={'HIDDEN'})
    ui_attach = BoolProperty(
        name="Assemble Model",  # Attach mesh to tag",
        description=("Place each body part on its parent tag\n"
                     "Can be used with multi selection imports or individual\n"
                     "Note: Make sure no duplicate tags are in scene. (eg loaded upper.md3 twice)"),
        default=True,
    )
    # Selected files
    files = CollectionProperty(
        type=bpy.types.PropertyGroup
    )

    def execute(self, context):
        import os

        if not (bpy.context.mode == 'OBJECT'):  # force mode
            bpy.ops.object.mode_set(mode='OBJECT')
        for ob in bpy.data.objects:  # deselect any objects
            set_select_state(context=ob, opt=False)

        from .import_md3 import MD3Importer_KP, MD3_Combine_KP

        # hy: multi model reader
        folder = (os.path.dirname(self.properties.filepath))
        for f in self.files:
            if not f or f.name == '':
                continue
            fPath = (os.path.join(folder, f.name))
            if os.path.exists(fPath):
                MD3Importer_KP(context)(fPath,  # self.properties.filepath,
                                        self.properties.ui_attach)
            else:
                self.report({'WARNING'}, "Warning: File Invalid")

        # attach to legs
        if self.properties.ui_attach:
            MD3_Combine_KP(context)()
        return {'FINISHED'}


class ExportMD3_KP(bpy.types.Operator, ExportHelper):
    '''Export a Quake 3 Model MD3 file'''
    bl_idname = "export_scene.md3"
    bl_label = 'Export MD3'
    filename_ext = ".md3"

    # filters
    filter_glob = StringProperty(default="*.md3", options={'HIDDEN'})
    texture_dir = StringProperty(default="textures/", name="Texture base path")

    def execute(self, context):
        try:
            from .export_md3 import MD3Exporter_KP
            MD3Exporter_KP(context, self.texture_dir)(self.properties.filepath)
            return {'FINISHED'}
        except struct.error:
            self.report({'ERROR'}, "Mesh does not fit within the MD3 model space." +
                        "Vertex axies locations must be below 512 blender units.")
        except ValueError as e:
            self.report({'ERROR'}, str(e))
        return {'CANCELLED'}


def menu_func_import(self, context):
    self.layout.operator(ImportMD3_KP.bl_idname, text="Quake 3 Model (.md3)-hy-")


def menu_func_export(self, context):
    self.layout.operator(ExportMD3_KP.bl_idname, text="Quake 3 Model (.md3)-hy-")


classes = (
    ExportMD3_KP,
    ImportMD3_KP
)


def register():
    for cls in classes:
        make_annotations(cls)  # backward compatable
        bpy.utils.register_class(cls)
    get_menu_import().append(menu_func_import)
    # get_menu_export().append(menu_func_export)  # hy: todo


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    get_menu_import().remove(menu_func_import)
    # get_menu_export().remove(menu_func_export)  # hy: todo


if __name__ == "__main__":
    register()
