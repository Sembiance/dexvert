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

# <pep8-80 compliant>

bl_info = {
    "name": "Blitz 3D format (.b3d)",
    "author": "Joric",
    "blender": (2, 80, 0),
    "location": "File > Import-Export",
    "description": "Import-Export B3D, meshes, uvs, materials, textures, "
                   "cameras & lamps",
    "warning": "",
    "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.6/Py/"
                "Scripts/Import-Export/Blitz3D_B3D",
    "support": 'OFFICIAL',
    "category": "Import-Export"}

if "bpy" in locals():
    import importlib
    if "import_b3d" in locals():
        importlib.reload(import_b3d)
    if "export_b3d" in locals():
        importlib.reload(export_b3d)


import bpy
from bpy.props import (
        BoolProperty,
        EnumProperty,
        FloatProperty,
        StringProperty,
        )
from bpy_extras.io_utils import (
        ImportHelper,
        ExportHelper,
        orientation_helper,
        axis_conversion,
        )


@orientation_helper(axis_forward='Y', axis_up='Z')
class ImportB3D(bpy.types.Operator, ImportHelper):
    """Import from B3D file format (.b3d)"""
    bl_idname = "import_scene.blitz3d_b3d"
    bl_label = 'Import B3D'
    bl_options = {'UNDO'}

    filename_ext = ".b3d"
    filter_glob : StringProperty(default="*.b3d", options={'HIDDEN'})

    constrain_size : FloatProperty(
            name="Size Constraint",
            description="Scale the model by 10 until it reaches the "
                        "size constraint (0 to disable)",
            min=0.0, max=1000.0,
            soft_min=0.0, soft_max=1000.0,
            default=10.0,
            )
    use_image_search : BoolProperty(
            name="Image Search",
            description="Search subdirectories for any associated images "
                        "(Warning, may be slow)",
            default=True,
            )
    use_apply_transform : BoolProperty(
            name="Apply Transform",
            description="Workaround for object transformations "
                        "importing incorrectly",
            default=True,
            )

    def execute(self, context):
        from . import import_b3d

        keywords = self.as_keywords(ignore=("axis_forward",
                                            "axis_up",
                                            "filter_glob",
                                            ))

        global_matrix = axis_conversion(from_forward=self.axis_forward,
                                        from_up=self.axis_up,
                                        ).to_4x4()
        keywords["global_matrix"] = global_matrix

        return import_b3d.load(self, context, **keywords)


@orientation_helper(axis_forward='Y', axis_up='Z')
class ExportB3D(bpy.types.Operator, ExportHelper):
    """Export to B3D file format (.b3d)"""
    bl_idname = "export_scene.blitz3d_b3d"
    bl_label = 'Export B3D'

    filename_ext = ".b3d"

    filter_glob: StringProperty(
            default="*.b3d",
            options={'HIDDEN'},
            )

    use_selection: BoolProperty(
            name="Selection Only",
            description="Export selected objects only",
            default=False,
            )

    def execute(self, context):
        from . import export_b3d

        keywords = self.as_keywords(ignore=("axis_forward",
                                            "axis_up",
                                            "filter_glob",
                                            "check_existing",
                                            ))
        global_matrix = axis_conversion(to_forward=self.axis_forward,
                                        to_up=self.axis_up,
                                        ).to_4x4()
        keywords["global_matrix"] = global_matrix

        return export_b3d.save(self, context, **keywords)


# Add to a menu
def menu_func_export(self, context):
    self.layout.operator(ExportB3D.bl_idname, text="Blitz3D (.b3d)")


def menu_func_import(self, context):
    self.layout.operator(ImportB3D.bl_idname, text="Blitz3D (.b3d)")


class DebugMacro(bpy.types.Operator):
    bl_idname = "object.debug_macro"
    bl_label = "Debug Macro"
    bl_options = {'REGISTER', 'UNDO'}

    from . import import_b3d
    from . import export_b3d

    filepath: bpy.props.StringProperty(name="filepath", default=import_b3d.filepath)

    def execute(self, context: bpy.context):
        import sys,imp

        print("b3d, loading", self.filepath)

        for material in bpy.data.materials:
            bpy.data.materials.remove(material)

        for obj in bpy.context.scene.objects:
            bpy.data.objects.remove(obj, do_unlink=True)

        module = sys.modules['io_scene_b3d']
        imp.reload(module)

        import_b3d.load(self, context, filepath=self.filepath)
        export_b3d.save(self, context, filepath=self.filepath.replace('.b3d','.exported.b3d'))

        """
        bpy.ops.view3d.viewnumpad(type='FRONT', align_active=False)

        bpy.ops.view3d.view_all(use_all_regions=True, center=True)

        if bpy.context.region_data.is_perspective:
            bpy.ops.view3d.view_persportho()
        """

        return {'FINISHED'}

addon_keymaps = []

classes = (
    ImportB3D,
    ExportB3D,
    DebugMacro
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)

    # handle the keymap
    wm = bpy.context.window_manager

    if wm.keyconfigs.addon:
        km = wm.keyconfigs.addon.keymaps.new(name="Window", space_type='EMPTY')
        kmi = km.keymap_items.new(DebugMacro.bl_idname, 'F', 'PRESS', ctrl=True, shift=True)
        addon_keymaps.append((km, kmi))


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)

    # handle the keymap
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    del addon_keymaps[:]

if __name__ == "__main__":
    register()
