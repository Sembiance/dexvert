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

# <pep8 compliant>

# Most of this has been copied from the __init__.py file for the io_scene__xx
# folders of the standard 2.59 blender package and customised to
# act as a wrapper for the conventional AC3D importer/exporter

import time
import datetime
from math import radians

import bpy
from bpy.types import Operator, TOPBAR_MT_file_import, TOPBAR_MT_file_export
from bpy.props import BoolProperty, EnumProperty, FloatProperty, \
    FloatVectorProperty, StringProperty
from bpy_extras.io_utils import ImportHelper, ExportHelper, axis_conversion
from mathutils import Euler

bl_info = {
    "name": "AC3D (.ac) format",
    "description": "Inivis AC3D model exporter for Blender.",
    "author": "Willian P Gerano, Chris Marr, Thomas Geymayer, Nikolai V. Chr., Scott Giese",
    "version": (5, 0),
    "blender": (4, 0, 0),
    "category": "Import-Export",
    "location": "File > Import-Export",
    "warning": "",
    "doc_url": (
        "http://wiki.flightgear.org/Blender_AC3D_import_and_export"
        "#Majic79_addon"),
    "tracker_url": "https://github.com/NikolaiVChr/Blender-AC3D/issues"
}

# To support reload properly, try to access a package var, if it's there,
# reload everything
if "bpy" in locals():
    import imp
    if 'import_ac3d' in locals():
        imp.reload(import_ac3d)
    if 'export_ac3d' in locals():
        imp.reload(export_ac3d)


def menu_func_import(self, context):
    self.layout.operator(AC3D_OT_Import.bl_idname, text='AC3D (.ac)')


def menu_func_export(self, context):
    self.layout.operator(AC3D_OT_Export.bl_idname, text='AC3D (.ac)')


class AC3D_OT_Import(Operator, ImportHelper):
    """Import from AC3D file format (.ac)"""
    bl_idname = 'import_scene.import_ac3d'
    bl_label = 'Import AC3D'
    bl_options = {'PRESET'}

    filename_ext = '.ac'

    filter_glob: StringProperty(
        default='*.ac',
        options={'HIDDEN'})

    axis_forward: EnumProperty(
        name="Forward",
        items=(
            ('X', "X Forward", ""),
            ('Y', "Y Forward", ""),
            ('Z', "Z Forward", ""),
            ('-X', "-X Forward", ""),
            ('-Y', "-Y Forward", ""),
            ('-Z', "-Z Forward", "")),
        default='-Z')

    axis_up: EnumProperty(
        name="Up",
        items=(
            ('X', "X Up", ""),
            ('Y', "Y Up", ""),
            ('Z', "Z Up", ""),
            ('-X', "-X Up", ""),
            ('-Y', "-Y Up", ""),
            ('-Z', "-Z Up", "")),
        default='Y')

    transparency_method: EnumProperty(
        name="Transparency Method",
        description="The transparency method that will be set in materials.",
        items=(
            ('MASK', "Mask", ""),
            ('Z_TRANSPARENCY', "Z Transparency", ""),
            ('RAYTRACE', "RayTrace", "")),
        default='Z_TRANSPARENCY')

#    use_emis_as_mircol: BoolProperty(
#        name="Set Emis to Mirror colour",
#        description="Set AC3D Emission colour into Blender Mirror colour",
#        default=False)

#    use_amb_as_mircol: BoolProperty(
#        name="Set Amb to Mirror colour",
#        description="Set AC3D Ambient colour into Blender Mirror colour",
#        default=False)

#    display_textured_solid: BoolProperty(
#        name="Display textured solid",
#        description=(
#            "Show textures applied when in Solid view (notice that "
#            "transparency for materials is then only seen in Material "
#            "view and Render view)"),
#        default=False)
        
    useEeveeSpecular: BoolProperty(
        name="Use Eevee Specular",
        description="Set materials to use Eevee Specular instead of Principled BSDF",
        default=False)


    rotation: FloatVectorProperty(
        description="Import Rotation",
        subtype="XYZ",
        unit="ROTATION",
        default=(0.0, 0.0, 0.0))

    translation: FloatVectorProperty(
        description="Import Location",
        subtype="TRANSLATION",
        unit="NONE",
        default=(0.0, 0.0, 0.0))

    parent_to: StringProperty(
        default="")

    collection_name: StringProperty(
        default="")

#    hide_hidden_objects : BoolProperty(
#        name="Hide hidden objects",
#        description=(
#            "Newer AC3D format supports hiding objects. If checked those "
#            "objects will be Restrict viewport visibility in Blender (wont "
#            "be seen until the small eye in Outliner is clicked)."
#        ),
#        default=True)

    def execute(self, context):
        from . import import_ac3d
        keywords = self.as_keywords(ignore=("axis_forward",
                                            "axis_up",
                                            "filter_glob",
                                            "rotation",
                                            "translation",
                                            "hide_props_region"))

        eul = Euler((radians(self.rotation[0]),
                     radians(self.rotation[1]),
                     radians(self.rotation[2])), 'XYZ')

        global_matrix = eul.to_matrix().to_4x4() @ \
            axis_conversion(from_forward=self.axis_forward,
                            from_up=self.axis_up).to_4x4()

        keywords["global_matrix"] = global_matrix

        t = time.mktime(datetime.datetime.now().timetuple())

        import_ac3d.AC3D_OT_Import(self, context, **keywords)

        t = time.mktime(datetime.datetime.now().timetuple()) - t
        print('Finished importing in', t, 'seconds')

        return {'FINISHED'}


#
#   The error message operator. When invoked, pops up a dialog
#   window with the given message.
#

class AC3D_OT_Message(Operator):
    bl_idname = "error.message"
    bl_label = "Message"
    type: StringProperty()
    message: StringProperty()

    def execute(self, context):
        self.report({'INFO'}, self.message)
        print(self.message)
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_popup(self, width=400, height=200)

    def draw(self, context):
        self.layout.label(text="A message has arrived")
        row = self.layout.split(factor=0.25)
        row.prop(self, "type")
        row.prop(self, "message")
        row = self.layout.split(factor=0.80)
        row.label(text="")
        row.operator("error")


#
#   The OK button in the error dialog
#

class AC3D_OT_Ok(Operator):
    bl_idname = "error.ok"
    bl_label = "OK"

    def execute(self, context):
        return {'FINISHED'}


class AC3D_OT_Export(Operator, ExportHelper):
    """Export to AC3D file format (.ac)"""
    bl_idname = 'export_scene.export_ac3d'
    bl_label = 'Export AC3D'
    bl_options = {'PRESET'}

    filename_ext = '.ac'

    v_info = bl_info["version"]

    filter_glob: StringProperty(
        default='*.ac',
        options={'HIDDEN'})

    axis_forward: EnumProperty(
        name="Forward",
        items=(('X', "X Forward", ""),
               ('Y', "Y Forward", ""),
               ('Z', "Z Forward", ""),
               ('-X', "-X Forward", ""),
               ('-Y', "-Y Forward", ""),
               ('-Z', "-Z Forward", "")),
        default='-Z'
    )

    axis_up: EnumProperty(
        name="Up",
        items=(('X', "X Up", ""),
               ('Y', "Y Up", ""),
               ('Z', "Z Up", ""),
               ('-X', "-X Up", ""),
               ('-Y', "-Y Up", ""),
               ('-Z', "-Z Up", "")),
        default='Y'
    )

    export_rots: EnumProperty(
        name="Matrices",
        description=(
            "Some loaders interpret the matrices wrong, to be safe, "
            "use Apply before Export."),
        items=(
            ('apply', "Apply before export", ""),
            ('export', "Export", "")),
        default='apply',
    )
    use_render_layers: BoolProperty(
        name="Only View Layers",
        description="Only export from selected view layers",
        default=True,
    )
    use_selection: BoolProperty(
        name="Selection Only",
        description="Export selected objects only",
        default=False,
    )
    merge_materials: BoolProperty(
        name="Merge materials",
        description="Merge materials that are identical",
        default=False,
    )
    global_doublesided: BoolProperty(
        name="Double sided",
        description="If all geometry in AC3D will be double sided or backface culled.",
        default=False,
    )
#    mircol_as_emis: BoolProperty(
#        name="Mirror col to Emis",
#        description="Export Blender mirror colour to AC3D emissive colour",
#        default=False,
#    )
#    mircol_as_amb: BoolProperty(
#        name="Mirror col to Amb",
#        description="Export Blender mirror colour to AC3D ambient colour",
#        default=False,
#    )
    amb_as_diff: BoolProperty(
        name="Amb same as Diff",
        description="Export AC3D ambient colour to be like Diffuse color",
        default=False,
    )
    export_lines: BoolProperty(
        name="Export lines",
        description=(
            "Export standalone edges, bezier curves etc. as AC3D lines. "
            "Will make export take longer."),
        default=False,
    )
    export_hidden: BoolProperty(
        name="Export hidden objects",
        description=(
            "Newer AC3D format supports hiding objects. If checked "
            "those objects will be exported as hidden. (notice that in older "
            "loaders they might show up, or the loader might choke on those "
            "new tokens)"),
        default=False,
    )
    export_lights: BoolProperty(
        name="Export lights",
        description=(
            "With this checked lights will also be exported. Notice "
            "they will all become pointlights. If not checked, any geometry "
            "that might have lamps as parent wont be output."),
        default=False,
    )
    crease_angle: FloatProperty(
        name="Default Crease Angle",
        description=(
            "Default crease/smooth angle for exported .ac "
            "faces that has not explicit set it."),
        default=radians(40.0),
        options={"ANIMATABLE"},
        unit="ROTATION",
        subtype="ANGLE",
    )

    def execute(self, context):
        if context.active_object:
            if context.active_object.mode == 'EDIT':
                print("AC3D was not exported due to being in edit mode.")
                bpy.ops.error.message(
                    'INVOKE_DEFAULT',
                    type="Error",
                    message='Cannot export AC3D in edit mode.')
                return {'FINISHED'}
        from . import export_ac3d
        keywords = self.as_keywords(ignore=("axis_forward",
                                            "axis_up",
                                            "filter_glob",
                                            "check_existing",
                                            "export_rots",
                                            ))

        global_matrix = axis_conversion(to_forward=self.axis_forward,
                                        to_up=self.axis_up,
                                        )
        keywords["global_matrix"] = global_matrix
        ex_rot = False
        if self.export_rots == 'export':
            ex_rot = True
        keywords["export_rot"] = ex_rot
        t = time.mktime(datetime.datetime.now().timetuple())
        export_ac3d.AC3D_OT_Export(self, context, **keywords)
        t = time.mktime(datetime.datetime.now().timetuple()) - t
        print('Finished exporting in', t, 'seconds')

        return {'FINISHED'}


__classes__ = (
    AC3D_OT_Export,
    AC3D_OT_Import,
    AC3D_OT_Message,
    AC3D_OT_Ok)


def register():
    for c in __classes__:
        bpy.utils.register_class(c)
    TOPBAR_MT_file_export.append(menu_func_export)
    TOPBAR_MT_file_import.append(menu_func_import)


def unregister():
    for c in reversed(__classes__):
        bpy.utils.unregister_class(c)
    TOPBAR_MT_file_export.remove(menu_func_export)
    TOPBAR_MT_file_import.remove(menu_func_import)


if __name__ == "__main__":
    register()
