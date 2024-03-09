from bpy.types import Operator
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy_extras.io_utils import ImportHelper
import bpy
from .xfile_importer import load

bl_info = {
    "name": "DirectX XFile format",
    "blender": (2, 80, 0),
    "category": "Import-Export",
}


def read_some_data(context, filepath, use_some_setting, type):
    load(filepath)
    return {'FINISHED'}


# ImportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.


class ImportSomeData(Operator, ImportHelper):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = "import_scene.x"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Import DirectX XFile"

    # ImportHelper mixin class uses this
    filename_ext = ".x"

    filter_glob: StringProperty(
        default="*.x",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    # List of operator properties, the attributes will be assigned
    # to the class instance from the operator settings before calling.
    use_setting: BoolProperty(
        name="Example Boolean",
        description="Example Tooltip",
        default=True,
    )

    type: EnumProperty(
        name="Example Enum",
        description="Choose between two items",
        items=(
            ('OPT_A', "First Option", "Description one"),
            ('OPT_B', "Second Option", "Description two"),
        ),
        default='OPT_A',
    )

    def execute(self, context):
        return read_some_data(context, self.filepath, self.use_setting, self.type)

# Only needed if you want to add into a dynamic menu


def menu_func_import(self, context):
    self.layout.operator(ImportSomeData.bl_idname, text="DirectX XFile (.x)")

# Register and add to the "file selector" menu (required to use F3 search "Text Import Operator" for quick access)


def register():
    bpy.utils.register_class(ImportSomeData)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)


def unregister():
    bpy.utils.unregister_class(ImportSomeData)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)


if __name__ == "__main__":
    register()
