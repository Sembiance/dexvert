# SPDX-License-Identifier: GPL-2.0-or-later
# Copyright (c)2011-2022 Alexander Nussbaumer

# <pep8 compliant>

###############################################################################
#234567890123456789012345678901234567890123456789012345678901234567890123456789
#--------1---------2---------3---------4---------5---------6---------7---------


#import python stuff
from random import (
        randrange,
        )


# import io_scene_ms3d stuff
from .ms3d_strings import (
        ms3d_str,
        )
from .ms3d_spec import (
        Ms3dSpec,
        )
from .ms3d_utils import (
        enable_edit_mode,
        get_edge_split_modifier_add_if,
        )


#import blender stuff
from bmesh import (
        from_edit_mesh,
        )
from bpy.utils import (
        register_class,
        unregister_class,
        )
from bpy_extras.io_utils import (
        ExportHelper,
        ImportHelper,
        )
from bpy.props import (
        BoolProperty,
        CollectionProperty,
        EnumProperty,
        FloatProperty,
        FloatVectorProperty,
        IntProperty,
        PointerProperty,
        StringProperty,
        )
from bpy.types import (
        Action,
        Armature,
        Bone,
        Collection,
        Material,
        Mesh,
        Operator,
        Panel,
        PropertyGroup,
        TOPBAR_MT_file_export,
        TOPBAR_MT_file_import,
        UIList,
        )
from bpy.app import (
        debug,
        )


class Ms3dUi:
    VERBOSE_MODE_NONE = 'NONE'
    VERBOSE_MODE_NORMAL = 'NORMAL'
    VERBOSE_MODE_MAXIMAL = 'MAXIMAL'

    VERBOSE_NONE = {}
    VERBOSE_NORMAL = {True, VERBOSE_MODE_NORMAL, VERBOSE_MODE_MAXIMAL, }
    VERBOSE_MAXIMAL = {True, VERBOSE_MODE_MAXIMAL, }

    DEFAULT_VERBOSE = VERBOSE_MODE_NONE


    ###########################################################################
    FLAG_TEXTURE_COMBINE_ALPHA = 'COMBINE_ALPHA'
    FLAG_TEXTURE_HAS_ALPHA = 'HAS_ALPHA'
    FLAG_TEXTURE_SPHERE_MAP = 'SPHERE_MAP'

    @staticmethod
    def texture_mode_from_ms3d(ms3d_value):
        ui_value = set()
        if (ms3d_value & Ms3dSpec.FLAG_TEXTURE_COMBINE_ALPHA) \
                == Ms3dSpec.FLAG_TEXTURE_COMBINE_ALPHA:
            ui_value.add(Ms3dUi.FLAG_TEXTURE_COMBINE_ALPHA)
        if (ms3d_value & Ms3dSpec.FLAG_TEXTURE_HAS_ALPHA) \
                == Ms3dSpec.FLAG_TEXTURE_HAS_ALPHA:
            ui_value.add(Ms3dUi.FLAG_TEXTURE_HAS_ALPHA)
        if (ms3d_value & Ms3dSpec.FLAG_TEXTURE_SPHERE_MAP) \
                == Ms3dSpec.FLAG_TEXTURE_SPHERE_MAP:
            ui_value.add(Ms3dUi.FLAG_TEXTURE_SPHERE_MAP)
        return ui_value

    @staticmethod
    def texture_mode_to_ms3d(ui_value):
        ms3d_value = Ms3dSpec.FLAG_TEXTURE_NONE

        if Ms3dUi.FLAG_TEXTURE_COMBINE_ALPHA in ui_value:
            ms3d_value |= Ms3dSpec.FLAG_TEXTURE_COMBINE_ALPHA
        if Ms3dUi.FLAG_TEXTURE_HAS_ALPHA in ui_value:
            ms3d_value |= Ms3dSpec.FLAG_TEXTURE_HAS_ALPHA
        if Ms3dUi.FLAG_TEXTURE_SPHERE_MAP in ui_value:
            ms3d_value |= Ms3dSpec.FLAG_TEXTURE_SPHERE_MAP
        return ms3d_value


    MODE_TRANSPARENCY_SIMPLE = 'SIMPLE'
    MODE_TRANSPARENCY_DEPTH_BUFFERED_WITH_ALPHA_REF \
            = 'DEPTH_BUFFERED_WITH_ALPHA_REF'
    MODE_TRANSPARENCY_DEPTH_SORTED_TRIANGLES = 'DEPTH_SORTED_TRIANGLES'

    @staticmethod
    def transparency_mode_from_ms3d(ms3d_value):
        if(ms3d_value == Ms3dSpec.MODE_TRANSPARENCY_SIMPLE):
            return Ms3dUi.MODE_TRANSPARENCY_SIMPLE
        elif(ms3d_value == \
                Ms3dSpec.MODE_TRANSPARENCY_DEPTH_BUFFERED_WITH_ALPHA_REF):
            return Ms3dUi.MODE_TRANSPARENCY_DEPTH_BUFFERED_WITH_ALPHA_REF
        elif(ms3d_value == Ms3dSpec.MODE_TRANSPARENCY_DEPTH_SORTED_TRIANGLES):
            return Ms3dUi.MODE_TRANSPARENCY_DEPTH_SORTED_TRIANGLES

        return Ms3dUi.MODE_TRANSPARENCY_SIMPLE

    @staticmethod
    def transparency_mode_to_ms3d(ui_value):
        if(ui_value == Ms3dUi.MODE_TRANSPARENCY_SIMPLE):
            return Ms3dSpec.MODE_TRANSPARENCY_SIMPLE
        elif(ui_value == Ms3dUi.MODE_TRANSPARENCY_DEPTH_BUFFERED_WITH_ALPHA_REF):
            return Ms3dSpec.MODE_TRANSPARENCY_DEPTH_BUFFERED_WITH_ALPHA_REF
        elif(ui_value == Ms3dUi.MODE_TRANSPARENCY_DEPTH_SORTED_TRIANGLES):
            return Ms3dSpec.MODE_TRANSPARENCY_DEPTH_SORTED_TRIANGLES

        return Ms3dSpec.MODE_TRANSPARENCY_SIMPLE


    FLAG_NONE = 'NONE'
    FLAG_SELECTED = 'SELECTED'
    FLAG_HIDDEN = 'HIDDEN'
    FLAG_SELECTED2 = 'SELECTED2'
    FLAG_DIRTY = 'DIRTY'
    FLAG_ISKEY = 'ISKEY'
    FLAG_NEWLYCREATED = 'NEWLYCREATED'
    FLAG_MARKED = 'MARKED'

    @staticmethod
    def flags_from_ms3d(ms3d_value):
        ui_value = set()
        if (ms3d_value & Ms3dSpec.FLAG_SELECTED) == Ms3dSpec.FLAG_SELECTED:
            ui_value.add(Ms3dUi.FLAG_SELECTED)
        if (ms3d_value & Ms3dSpec.FLAG_HIDDEN) == Ms3dSpec.FLAG_HIDDEN:
            ui_value.add(Ms3dUi.FLAG_HIDDEN)
        if (ms3d_value & Ms3dSpec.FLAG_SELECTED2) == Ms3dSpec.FLAG_SELECTED2:
            ui_value.add(Ms3dUi.FLAG_SELECTED2)
        if (ms3d_value & Ms3dSpec.FLAG_DIRTY) == Ms3dSpec.FLAG_DIRTY:
            ui_value.add(Ms3dUi.FLAG_DIRTY)
        if (ms3d_value & Ms3dSpec.FLAG_ISKEY) == Ms3dSpec.FLAG_ISKEY:
            ui_value.add(Ms3dUi.FLAG_ISKEY)
        if (ms3d_value & Ms3dSpec.FLAG_NEWLYCREATED) == \
                Ms3dSpec.FLAG_NEWLYCREATED:
            ui_value.add(Ms3dUi.FLAG_NEWLYCREATED)
        if (ms3d_value & Ms3dSpec.FLAG_MARKED) == Ms3dSpec.FLAG_MARKED:
            ui_value.add(Ms3dUi.FLAG_MARKED)
        return ui_value

    @staticmethod
    def flags_to_ms3d(ui_value):
        ms3d_value = Ms3dSpec.FLAG_NONE
        if Ms3dUi.FLAG_SELECTED in ui_value:
            ms3d_value |= Ms3dSpec.FLAG_SELECTED
        if Ms3dUi.FLAG_HIDDEN in ui_value:
            ms3d_value |= Ms3dSpec.FLAG_HIDDEN
        if Ms3dUi.FLAG_SELECTED2 in ui_value:
            ms3d_value |= Ms3dSpec.FLAG_SELECTED2
        if Ms3dUi.FLAG_DIRTY in ui_value:
            ms3d_value |= Ms3dSpec.FLAG_DIRTY
        if Ms3dUi.FLAG_ISKEY in ui_value:
            ms3d_value |= Ms3dSpec.FLAG_ISKEY
        if Ms3dUi.FLAG_NEWLYCREATED in ui_value:
            ms3d_value |= Ms3dSpec.FLAG_NEWLYCREATED
        if Ms3dUi.FLAG_MARKED in ui_value:
            ms3d_value |= Ms3dSpec.FLAG_MARKED
        return ms3d_value

    ###########################################################################
    ICON_OPTIONS = 'OPTIONS'
    ICON_OBJECT = 'WORLD'
    ICON_PROCESSING = 'OBJECT_DATA'
    ICON_MODIFIER = 'MODIFIER_DATA'
    ICON_ANIMATION = 'ARMATURE_DATA'
    ICON_ROTATION_MODE = 'BONE_DATA'
    ICON_ERROR = 'ERROR'
    ICON_VERBOSE = 'SPEAKER'
    ICON_ACTIVE = 'PIVOT_ACTIVE'

    ###########################################################################
    PROP_DEFAULT_VERBOSE = DEFAULT_VERBOSE

    ###########################################################################
    PROP_DEFAULT_USE_JOINT_SIZE = False
    PROP_DEFAULT_JOINT_SIZE = 0.01
    PROP_JOINT_SIZE_MIN = 0.01
    PROP_JOINT_SIZE_MAX = 10.0
    PROP_JOINT_SIZE_STEP = 0.1
    PROP_JOINT_SIZE_PRECISION = 2

    ###########################################################################
    PROP_DEFAULT_USE_ANIMATION = True
    PROP_DEFAULT_NORMALIZE_WEIGHTS = True
    PROP_DEFAULT_SHRINK_TO_KEYS = False
    PROP_DEFAULT_BAKE_EACH_FRAME = True
    PROP_DEFAULT_JOINT_TO_BONES = False
    PROP_DEFAULT_USE_BLENDER_NAMES = True
    PROP_DEFAULT_USE_BLENDER_MATERIALS = False
    PROP_DEFAULT_EXTENDED_NORMAL_HANDLING = False
    PROP_DEFAULT_APPLY_TRANSFORM = True
    PROP_DEFAULT_APPLY_MODIFIERS = True

    ###########################################################################
    PROP_ITEM_APPLY_MODIFIERS_MODE_VIEW = 'PREVIEW'
    PROP_ITEM_APPLY_MODIFIERS_MODE_RENDER = 'RENDER'
    PROP_DEFAULT_APPLY_MODIFIERS_MODE = PROP_ITEM_APPLY_MODIFIERS_MODE_VIEW

    ###########################################################################
    PROP_ITEM_ROTATION_MODE_EULER = 'EULER'
    PROP_ITEM_ROTATION_MODE_QUATERNION = 'QUATERNION'
    PROP_DEFAULT_ANIMATION_ROTATION = PROP_ITEM_ROTATION_MODE_EULER

    ###########################################################################
    OPT_SMOOTHING_GROUP_APPLY = 'io_scene_ms3d.apply_smoothing_group'
    OPT_GROUP_APPLY = 'io_scene_ms3d.apply_group'
    OPT_MATERIAL_APPLY = 'io_scene_ms3d.apply_material'


###############################################################################
class Ms3dArmatureProperties(PropertyGroup):
    name: StringProperty(
            name=ms3d_str['PROP_NAME_NAME'],
            description=ms3d_str['PROP_DESC_NAME_ARMATURE'],
            default="",
            #options={'HIDDEN', },
            )

class Ms3dGroupProperties(PropertyGroup):
    name: StringProperty(
            name=ms3d_str['PROP_NAME_NAME'],
            description=ms3d_str['PROP_DESC_GROUP_NAME'],
            default="",
            #options={'HIDDEN', },
            )

    flags: EnumProperty(
            name=ms3d_str['PROP_NAME_FLAGS'],
            description=ms3d_str['PROP_DESC_FLAGS_GROUP'],
            items=(#(Ms3dUi.FLAG_NONE, ms3d_str['ENUM_FLAG_NONE_1'],
                   #         ms3d_str['ENUM_FLAG_NONE_2'],
                   #         Ms3dSpec.FLAG_NONE),
                    (Ms3dUi.FLAG_SELECTED,
                            ms3d_str['ENUM_FLAG_SELECTED_1'],
                            ms3d_str['ENUM_FLAG_SELECTED_2'],
                            Ms3dSpec.FLAG_SELECTED),
                    (Ms3dUi.FLAG_HIDDEN,
                            ms3d_str['ENUM_FLAG_HIDDEN_1'],
                            ms3d_str['ENUM_FLAG_HIDDEN_2'],
                            Ms3dSpec.FLAG_HIDDEN),
                    (Ms3dUi.FLAG_SELECTED2,
                            ms3d_str['ENUM_FLAG_SELECTED2_1'],
                            ms3d_str['ENUM_FLAG_SELECTED2_2'],
                            Ms3dSpec.FLAG_SELECTED2),
                    (Ms3dUi.FLAG_DIRTY,
                            ms3d_str['ENUM_FLAG_DIRTY_1'],
                            ms3d_str['ENUM_FLAG_DIRTY_2'],
                            Ms3dSpec.FLAG_DIRTY),
                    (Ms3dUi.FLAG_ISKEY,
                            ms3d_str['ENUM_FLAG_ISKEY_1'],
                            ms3d_str['ENUM_FLAG_ISKEY_2'],
                            Ms3dSpec.FLAG_ISKEY),
                    (Ms3dUi.FLAG_NEWLYCREATED,
                            ms3d_str['ENUM_FLAG_NEWLYCREATED_1'],
                            ms3d_str['ENUM_FLAG_NEWLYCREATED_2'],
                            Ms3dSpec.FLAG_NEWLYCREATED),
                    (Ms3dUi.FLAG_MARKED,
                            ms3d_str['ENUM_FLAG_MARKED_1'],
                            ms3d_str['ENUM_FLAG_MARKED_2'],
                            Ms3dSpec.FLAG_MARKED),
                    ),
            default=Ms3dUi.flags_from_ms3d(Ms3dSpec.DEFAULT_FLAGS),
            options={'ENUM_FLAG', 'ANIMATABLE', },
            )

    comment: StringProperty(
            name=ms3d_str['PROP_NAME_COMMENT'],
            description=ms3d_str['PROP_DESC_COMMENT_GROUP'],
            default="",
            #options={'HIDDEN', },
            )

    id: IntProperty(options={'HIDDEN', },)

class Ms3dJointProperties(PropertyGroup):
    name: StringProperty(
            name=ms3d_str['PROP_NAME_NAME'],
            description=ms3d_str['PROP_DESC_NAME_JOINT'],
            default="",
            #options={'HIDDEN', },
            )

    flags: EnumProperty(
            name=ms3d_str['PROP_NAME_FLAGS'],
            description=ms3d_str['PROP_DESC_FLAGS_JOINT'],
            items=(#(Ms3dUi.FLAG_NONE,
                   #         ms3d_str['ENUM_FLAG_NONE_1'],
                   #         ms3d_str['ENUM_FLAG_NONE_2'],
                   #         Ms3dSpec.FLAG_NONE),
                    (Ms3dUi.FLAG_SELECTED,
                            ms3d_str['ENUM_FLAG_SELECTED_1'],
                            ms3d_str['ENUM_FLAG_SELECTED_2'],
                            Ms3dSpec.FLAG_SELECTED),
                    (Ms3dUi.FLAG_HIDDEN,
                            ms3d_str['ENUM_FLAG_HIDDEN_1'],
                            ms3d_str['ENUM_FLAG_HIDDEN_2'],
                            Ms3dSpec.FLAG_HIDDEN),
                    (Ms3dUi.FLAG_SELECTED2,
                            ms3d_str['ENUM_FLAG_SELECTED2_1'],
                            ms3d_str['ENUM_FLAG_SELECTED2_2'],
                            Ms3dSpec.FLAG_SELECTED2),
                    (Ms3dUi.FLAG_DIRTY,
                            ms3d_str['ENUM_FLAG_DIRTY_1'],
                            ms3d_str['ENUM_FLAG_DIRTY_2'],
                            Ms3dSpec.FLAG_DIRTY),
                    (Ms3dUi.FLAG_ISKEY,
                            ms3d_str['ENUM_FLAG_ISKEY_1'],
                            ms3d_str['ENUM_FLAG_ISKEY_2'],
                            Ms3dSpec.FLAG_ISKEY),
                    (Ms3dUi.FLAG_NEWLYCREATED,
                            ms3d_str['ENUM_FLAG_NEWLYCREATED_1'],
                            ms3d_str['ENUM_FLAG_NEWLYCREATED_2'],
                            Ms3dSpec.FLAG_NEWLYCREATED),
                    (Ms3dUi.FLAG_MARKED,
                            ms3d_str['ENUM_FLAG_MARKED_1'],
                            ms3d_str['ENUM_FLAG_MARKED_2'],
                            Ms3dSpec.FLAG_MARKED),
                    ),
            default=Ms3dUi.flags_from_ms3d(Ms3dSpec.DEFAULT_FLAGS),
            options={'ENUM_FLAG', 'ANIMATABLE', },
            )

    color: FloatVectorProperty(
            name=ms3d_str['PROP_NAME_COLOR'],
            description=ms3d_str['PROP_DESC_COLOR_JOINT'],
            subtype='COLOR', size=3, min=0, max=1, precision=3, step=0.1,
            default=Ms3dSpec.DEFAULT_JOINT_COLOR,
            #options={'HIDDEN', },
            )

    comment: StringProperty(
            name=ms3d_str['PROP_NAME_COMMENT'],
            description=ms3d_str['PROP_DESC_COMMENT_JOINT'],
            default="",
            #options={'HIDDEN', },
            )

class Ms3dMaterialHelper:
    @staticmethod
    def copy_to_blender_ambient(_cls, _blender_context):
        pass

    @staticmethod
    def copy_to_blender_diffuse(_cls, _blender_context):
        pass

    @staticmethod
    def copy_to_blender_specular(_cls, _blender_context):
        pass

    @staticmethod
    def copy_to_blender_emissive(_cls, _blender_context):
        pass

    @staticmethod
    def copy_to_blender_shininess(_cls, _blender_context):
        pass

    @staticmethod
    def copy_to_blender_transparency(_cls, _blender_context):
        pass


    @staticmethod
    def copy_from_blender(_cls, _blender_context, _ms3d_material, _blender_material):
        pass

class Ms3dMaterialProperties(PropertyGroup):
    name: StringProperty(
            name=ms3d_str['PROP_NAME_NAME'],
            description=ms3d_str['PROP_DESC_NAME_MATERIAL'],
            default="",
            #options={'HIDDEN', },
            )

    ambient: FloatVectorProperty(
            name=ms3d_str['PROP_NAME_AMBIENT'],
            description=ms3d_str['PROP_DESC_AMBIENT'],
            subtype='COLOR', size=4, min=0, max=1, precision=3, step=0.1,
            default=Ms3dSpec.DEFAULT_MATERIAL_AMBIENT,
            update=Ms3dMaterialHelper.copy_to_blender_ambient,
            #options={'HIDDEN', },
            )

    diffuse: FloatVectorProperty(
            name=ms3d_str['PROP_NAME_DIFFUSE'],
            description=ms3d_str['PROP_DESC_DIFFUSE'],
            subtype='COLOR', size=4, min=0, max=1, precision=3, step=0.1,
            default=Ms3dSpec.DEFAULT_MATERIAL_DIFFUSE,
            update=Ms3dMaterialHelper.copy_to_blender_diffuse,
            #options={'HIDDEN', },
            )

    specular: FloatVectorProperty(
            name=ms3d_str['PROP_NAME_SPECULAR'],
            description=ms3d_str['PROP_DESC_SPECULAR'],
            subtype='COLOR', size=4, min=0, max=1, precision=3, step=0.1,
            default=Ms3dSpec.DEFAULT_MATERIAL_SPECULAR,
            update=Ms3dMaterialHelper.copy_to_blender_specular,
            #options={'HIDDEN', },
            )

    emissive: FloatVectorProperty(
            name=ms3d_str['PROP_NAME_EMISSIVE'],
            description=ms3d_str['PROP_DESC_EMISSIVE'],
            subtype='COLOR', size=4, min=0, max=1, precision=3, step=0.1,
            default=Ms3dSpec.DEFAULT_MATERIAL_EMISSIVE,
            update=Ms3dMaterialHelper.copy_to_blender_emissive,
            #options={'HIDDEN', },
            )

    shininess: FloatProperty(
            name=ms3d_str['PROP_NAME_SHININESS'],
            description=ms3d_str['PROP_DESC_SHININESS'],
            min=0, max=Ms3dSpec.MAX_MATERIAL_SHININESS, precision=3, step=0.1,
            default=Ms3dSpec.DEFAULT_MATERIAL_SHININESS,
            subtype='FACTOR',
            update=Ms3dMaterialHelper.copy_to_blender_shininess,
            #options={'HIDDEN', },
            )

    transparency: FloatProperty(
            name=ms3d_str['PROP_NAME_TRANSPARENCY'],
            description=ms3d_str['PROP_DESC_TRANSPARENCY'],
            min=0, max=1, precision=3, step=0.1,
            default=0,
            subtype='FACTOR',
            update=Ms3dMaterialHelper.copy_to_blender_transparency,
            #options={'HIDDEN', },
            )

    mode: EnumProperty(
            name=ms3d_str['PROP_NAME_MODE'],
            description=ms3d_str['PROP_DESC_MODE_TEXTURE'],
            items=( (Ms3dUi.FLAG_TEXTURE_COMBINE_ALPHA,
                            ms3d_str['PROP_FLAG_TEXTURE_COMBINE_ALPHA_1'],
                            ms3d_str['PROP_FLAG_TEXTURE_COMBINE_ALPHA_2'],
                            Ms3dSpec.FLAG_TEXTURE_COMBINE_ALPHA),
                    (Ms3dUi.FLAG_TEXTURE_HAS_ALPHA,
                            ms3d_str['PROP_FLAG_TEXTURE_HAS_ALPHA_1'],
                            ms3d_str['PROP_FLAG_TEXTURE_HAS_ALPHA_2'],
                            Ms3dSpec.FLAG_TEXTURE_HAS_ALPHA),
                    (Ms3dUi.FLAG_TEXTURE_SPHERE_MAP,
                            ms3d_str['PROP_FLAG_TEXTURE_SPHERE_MAP_1'],
                            ms3d_str['PROP_FLAG_TEXTURE_SPHERE_MAP_2'],
                            Ms3dSpec.FLAG_TEXTURE_SPHERE_MAP),
                    ),
            default=Ms3dUi.texture_mode_from_ms3d(
                    Ms3dSpec.DEFAULT_MATERIAL_MODE),
            options={'ANIMATABLE', 'ENUM_FLAG', },
            )

    texture: StringProperty(
            name=ms3d_str['PROP_NAME_TEXTURE'],
            description=ms3d_str['PROP_DESC_TEXTURE'],
            default="",
            subtype = 'FILE_PATH'
            #options={'HIDDEN', },
            )

    alphamap: StringProperty(
            name=ms3d_str['PROP_NAME_ALPHAMAP'],
            description=ms3d_str['PROP_DESC_ALPHAMAP'],
            default="",
            subtype = 'FILE_PATH'
            #options={'HIDDEN', },
            )

    comment: StringProperty(
            name=ms3d_str['PROP_NAME_COMMENT'],
            description=ms3d_str['PROP_DESC_COMMENT_MATERIAL'],
            default="",
            #options={'HIDDEN', },
            )

class Ms3dModelProperties(PropertyGroup):
    name: StringProperty(
            name=ms3d_str['PROP_NAME_NAME'],
            description=ms3d_str['PROP_DESC_NAME_MODEL'],
            default="",
            #options={'HIDDEN', },
            )

    joint_size: FloatProperty(
            name=ms3d_str['PROP_NAME_JOINT_SIZE'],
            description=ms3d_str['PROP_DESC_JOINT_SIZE'],
            min=Ms3dUi.PROP_JOINT_SIZE_MIN, max=Ms3dUi.PROP_JOINT_SIZE_MAX,
            precision=Ms3dUi.PROP_JOINT_SIZE_PRECISION, \
                    step=Ms3dUi.PROP_JOINT_SIZE_STEP,
            default=Ms3dUi.PROP_DEFAULT_JOINT_SIZE,
            subtype='FACTOR',
            #options={'HIDDEN', },
            )

    transparency_mode: EnumProperty(
            name=ms3d_str['PROP_NAME_TRANSPARENCY_MODE'],
            description=ms3d_str['PROP_DESC_TRANSPARENCY_MODE'],
            items=( (Ms3dUi.MODE_TRANSPARENCY_SIMPLE,
                            ms3d_str['PROP_MODE_TRANSPARENCY_SIMPLE_1'],
                            ms3d_str['PROP_MODE_TRANSPARENCY_SIMPLE_2'],
                            Ms3dSpec.MODE_TRANSPARENCY_SIMPLE),
                    (Ms3dUi.MODE_TRANSPARENCY_DEPTH_SORTED_TRIANGLES,
                            ms3d_str['PROP_MODE_TRANSPARENCY_DEPTH_SORTED_TRIANGLES_1'],
                            ms3d_str['PROP_MODE_TRANSPARENCY_DEPTH_SORTED_TRIANGLES_2'],
                            Ms3dSpec.MODE_TRANSPARENCY_DEPTH_SORTED_TRIANGLES),
                    (Ms3dUi.MODE_TRANSPARENCY_DEPTH_BUFFERED_WITH_ALPHA_REF,
                            ms3d_str['PROP_MODE_TRANSPARENCY_DEPTH_BUFFERED_WITH_ALPHA_REF_1'],
                            ms3d_str['PROP_MODE_TRANSPARENCY_DEPTH_BUFFERED_WITH_ALPHA_REF_2'],
                            Ms3dSpec.MODE_TRANSPARENCY_DEPTH_BUFFERED_WITH_ALPHA_REF),
                    ),
            default=Ms3dUi.transparency_mode_from_ms3d(
                    Ms3dSpec.DEFAULT_MODEL_TRANSPARENCY_MODE),
            #options={'HIDDEN', },
            )

    alpha_ref: FloatProperty(
            name=ms3d_str['PROP_NAME_ALPHA_REF'],
            description=ms3d_str['PROP_DESC_ALPHA_REF'],
            min=0, max=1, precision=3, step=0.1,
            default=0.5,
            subtype='FACTOR',
            #options={'HIDDEN', },
            )

    comment: StringProperty(
            name=ms3d_str['PROP_NAME_COMMENT'],
            description=ms3d_str['PROP_DESC_COMMENT_MODEL'],
            default="",
            #options={'HIDDEN', },
            )

    ##########################
    # ms3d group handling
    #
    apply_mode: EnumProperty(
            items=( ('ASSIGN',
                            ms3d_str['ENUM_ASSIGN_1'],
                            ms3d_str['ENUM_ASSIGN_2_SMOOTHING_GROUP']),
                    ('SELECT',
                            ms3d_str['ENUM_SELECT_1'],
                            ms3d_str['ENUM_SELECT_2_SMOOTHING_GROUP']),
                    ('DESELECT',
                            ms3d_str['ENUM_DESELECT_1'],
                            ms3d_str['ENUM_DESELECT_2_SMOOTHING_GROUP']),
                    ),
            default='SELECT',
            options={'HIDDEN', 'SKIP_SAVE', },
            )

    selected_group_index: IntProperty(
            default=-1,
            min=-1,
            options={'HIDDEN', 'SKIP_SAVE', },
            )
    #
    # ms3d group handling
    ##########################

    groups: CollectionProperty(
            type=Ms3dGroupProperties,
            #options={'HIDDEN', },
            )


    def generate_unique_id(self):
        return randrange(1, 0x7FFFFFFF) # pseudo unique id

    def create_group(self):
        item = self.groups.add()
        item.id = self.generate_unique_id()
        length = len(self.groups)
        self.selected_group_index = length - 1

        item.name = ms3d_str['STRING_FORMAT_GROUP'].format(length)
        return item

    def remove_group(self):
        index = self.selected_group_index
        length = len(self.groups)
        if (index >= 0) and (index < length):
            if index > 0 or length == 1:
                self.selected_group_index = index - 1
            self.groups.remove(index)


###############################################################################
class DATA_OT_ms3d_apply_smoothing_group(Operator):
    bl_idname = Ms3dUi.OPT_SMOOTHING_GROUP_APPLY
    bl_label = ms3d_str['BL_LABEL_SMOOTHING_GROUP_OPERATOR']
    bl_options = {'UNDO', 'INTERNAL', }
    bl_order = 101

    smoothing_group_index: IntProperty(
            name=ms3d_str['PROP_SMOOTHING_GROUP_INDEX'],
            options={'HIDDEN', 'SKIP_SAVE', },
            )

    @classmethod
    def poll(cls, blender_context):
        return (blender_context
                and blender_context.object
                and blender_context.object.type in {'MESH', }
                and blender_context.object.data
                and blender_context.object.data.ms3d is not None
                and blender_context.mode == 'EDIT_MESH'
                and blender_context.tool_settings.mesh_select_mode[2]
                )

    def execute(self, blender_context):
        custom_data = blender_context.object.data.ms3d
        blender_mesh = blender_context.object.data
        bm = from_edit_mesh(blender_mesh)
        layer_smoothing_group = bm.faces.layers.int.get(
                ms3d_str['OBJECT_LAYER_SMOOTHING_GROUP'])
        if custom_data.apply_mode in {'SELECT', 'DESELECT', }:
            if layer_smoothing_group is not None:
                is_select = (custom_data.apply_mode == 'SELECT')
                for bmf in bm.faces:
                    if (bmf[layer_smoothing_group] \
                            == self.smoothing_group_index):
                        bmf.select_set(is_select)
        elif custom_data.apply_mode == 'ASSIGN':
            if layer_smoothing_group is None:
                layer_smoothing_group = bm.faces.layers.int.new(
                        ms3d_str['OBJECT_LAYER_SMOOTHING_GROUP'])
                blender_mesh_object = blender_context.object
                get_edge_split_modifier_add_if(blender_mesh_object)
            blender_face_list = []
            for bmf in bm.faces:
                if not bmf.smooth:
                    bmf.smooth = True
                if bmf.select:
                    bmf[layer_smoothing_group] = self.smoothing_group_index
                    blender_face_list.append(bmf)
            edge_dict = {}
            for bmf in blender_face_list:
                bmf.smooth = True
                for bme in bmf.edges:
                    if edge_dict.get(bme) is None:
                        edge_dict[bme] = 0
                    else:
                        edge_dict[bme] += 1
                    is_border = (edge_dict[bme] == 0)
                    if is_border:
                        surround_face_smoothing_group_index \
                                = self.smoothing_group_index
                        for bmf in bme.link_faces:
                            if bmf[layer_smoothing_group] \
                                    != surround_face_smoothing_group_index:
                                surround_face_smoothing_group_index \
                                        = bmf[layer_smoothing_group]
                                break;
                        if surround_face_smoothing_group_index \
                                == self.smoothing_group_index:
                            is_border = False
                    bme.seam = is_border
                    bme.smooth = not is_border
        bm.free()
        enable_edit_mode(False, blender_context)
        enable_edit_mode(True, blender_context)
        return {'FINISHED', }

class DATA_OT_ms3d_apply_group(Operator):
    bl_idname = Ms3dUi.OPT_GROUP_APPLY
    bl_label = ms3d_str['BL_LABEL_GROUP_OPERATOR']
    bl_options = {'UNDO', 'INTERNAL', }
    bl_order = 101

    mode: EnumProperty(
            items=( ('', "", ""),
                    ('ADD_GROUP',
                            ms3d_str['ENUM_ADD_GROUP_1'],
                            ms3d_str['ENUM_ADD_GROUP_2']),
                    ('REMOVE_GROUP',
                            ms3d_str['ENUM_REMOVE_GROUP_1'],
                            ms3d_str['ENUM_REMOVE_GROUP_2']),
                    ('ASSIGN',
                            ms3d_str['ENUM_ASSIGN_1'],
                            ms3d_str['ENUM_ASSIGN_2_GROUP']),
                    ('REMOVE',
                            ms3d_str['ENUM_REMOVE_1'],
                            ms3d_str['ENUM_REMOVE_2_GROUP']),
                    ('SELECT',
                            ms3d_str['ENUM_SELECT_1'],
                            ms3d_str['ENUM_SELECT_2_GROUP']),
                    ('DESELECT',
                            ms3d_str['ENUM_DESELECT_1'],
                            ms3d_str['ENUM_DESELECT_2_GROUP']),
                    ),
            options={'HIDDEN', 'SKIP_SAVE', },
            )

    @classmethod
    def poll(cls, blender_context):
        return (blender_context
                and blender_context.object
                and blender_context.object.type in {'MESH', }
                and blender_context.object.data
                and blender_context.object.data.ms3d is not None
                and blender_context.mode == 'EDIT_MESH'
                #and blender_context.object.data.ms3d.selected_group_index != -1
                )

    def execute(self, blender_context):
        custom_data = blender_context.object.data.ms3d
        blender_mesh = blender_context.object.data
        bm = None
        bm = from_edit_mesh(blender_mesh)

        if self.mode == 'ADD_GROUP':
            item = custom_data.create_group()
            layer_group = bm.faces.layers.int.get(
                    ms3d_str['OBJECT_LAYER_GROUP'])
            if layer_group is None:
                bm.faces.layers.int.new(ms3d_str['OBJECT_LAYER_GROUP'])

        elif self.mode == 'REMOVE_GROUP':
            custom_data.remove_group()

        elif (custom_data.selected_group_index >= 0) and (
                custom_data.selected_group_index < len(custom_data.groups)):
            if self.mode in {'SELECT', 'DESELECT', }:
                layer_group = bm.faces.layers.int.get(
                        ms3d_str['OBJECT_LAYER_GROUP'])
                if layer_group is not None:
                    is_select = (self.mode == 'SELECT')
                    id = custom_data.groups[
                            custom_data.selected_group_index].id
                    for bmf in bm.faces:
                        if bmf[layer_group] == id:
                            bmf.select_set(is_select)

            elif self.mode in {'ASSIGN', 'REMOVE', }:
                layer_group = bm.faces.layers.int.get(
                        ms3d_str['OBJECT_LAYER_GROUP'])
                if layer_group is None:
                    layer_group = bm.faces.layers.int.new(
                            ms3d_str['OBJECT_LAYER_GROUP'])

                is_assign = (self.mode == 'ASSIGN')
                id = custom_data.groups[custom_data.selected_group_index].id
                for bmf in bm.faces:
                    if bmf.select:
                        if is_assign:
                            bmf[layer_group] = id
                        else:
                            bmf[layer_group] = -1
        if bm is not None:
            bm.free()
        enable_edit_mode(False, blender_context)
        enable_edit_mode(True, blender_context)
        return {'FINISHED', }

class MATERIAL_OT_ms3d_apply_material(Operator):
    bl_idname = Ms3dUi.OPT_MATERIAL_APPLY
    bl_label = ms3d_str['BL_LABEL_MATERIAL_OPERATOR']
    bl_options = {'UNDO', 'INTERNAL', }
    bl_order = 101

    mode: EnumProperty(
            items=( ('', "", ""),
                    ('FROM_BLENDER',
                            ms3d_str['ENUM_FROM_BLENDER_1'],
                            ms3d_str['ENUM_FROM_BLENDER_2']),
                    ('TO_BLENDER',
                            ms3d_str['ENUM_TO_BLENDER_1'],
                            ms3d_str['ENUM_TO_BLENDER_2']),
                    ),
            options={'HIDDEN', 'SKIP_SAVE', },
            )

    @classmethod
    def poll(cls, blender_context):
        return (blender_context
                and blender_context.object
                and blender_context.object.type in {'MESH', }
                and blender_context.object.data
                and blender_context.object.data.ms3d is not None
                and blender_context.material
                and blender_context.material.ms3d is not None
                )

    def execute(self, blender_context):
        blender_material = blender_context.active_object.active_material
        ms3d_material = blender_material.ms3d

        if self.mode == 'FROM_BLENDER':
            # not implemented
            pass

        elif self.mode == 'TO_BLENDER':
            # not implemented
            pass

        return {'FINISHED', }

    # entrypoint for option via UI
    def invoke(self, blender_context, _event):
        return blender_context.window_manager.invoke_props_dialog(self)


###############################################################################
# http://www.blender.org/documentation/blender_python_api_2_65_10/bpy.types.UIList.html
#
# uiList: ctrl-clic-edit name
# http://lists.blender.org/pipermail/bf-committers/2013-November/042113.html
# http://git.blender.org/gitweb/gitweb.cgi/blender.git/commit/f842ce82e6c92b156c0036cbefb4e4d97cd1d498
# http://git.blender.org/gitweb/gitweb.cgi/blender.git/commit/4c52e737df39e538d3b41a232035a4a1e240505d
# https://docs.blender.org/api/current/bpy.types.UIList.html?highlight=uilist
class DATA_UL_ms3d_group(UIList):
    def draw_item(self, _context, layout, _data, item, icon, _active_data, _active_propname, _index):
        if self.layout_type in {'DEFAULT', 'COMPACT', }:
            if item:
                layout.prop(item, "name", text="", emboss=False, icon_value=icon)
            else:
                layout.label(icon_value=icon)
        elif self.layout_type in {'GRID', }:
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)

###############################################################################
class OBJECT_PT_ms3d_mesh(Panel):
    bl_idname = 'OBJECT_PT_Ms3dMesh'
    bl_label = ms3d_str['LABEL_PANEL_MODEL']
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'object'
    bl_order = 101

    @classmethod
    def poll(cls, blender_context):
        return (blender_context
                and blender_context.object
                and blender_context.object.type in {'MESH', }
                and blender_context.object.data
                and blender_context.object.data.ms3d is not None
                )

    def draw_header(self, _blender_context):
        layout = self.layout
        layout.label(icon='PLUGIN')

    def draw(self, blender_context):
        layout = self.layout
        custom_data = blender_context.object.data.ms3d

        row = layout.row()
        row.prop(custom_data, 'name')

        col = layout.column()
        row = col.row()
        row.prop(custom_data, 'joint_size')
        row = col.row()
        row.prop(custom_data, 'transparency_mode')
        row = col.row()
        row.prop(custom_data, 'alpha_ref', )

        row = layout.row()
        row.prop(custom_data, 'comment')

class MATERIAL_PT_ms3d_material(Panel):
    bl_label = ms3d_str['LABEL_PANEL_MATERIALS']
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'material'
    bl_order = 101

    @classmethod
    def poll(cls, blender_context):
        return (blender_context
                and blender_context.object
                and blender_context.object.type in {'MESH', }
                and blender_context.object.data
                and blender_context.object.data.ms3d is not None
                and blender_context.material
                and blender_context.material.ms3d is not None
                )

    def draw_header(self, _blender_context):
        layout = self.layout
        layout.label(icon='PLUGIN')

    def draw(self, blender_context):
        layout = self.layout
        custom_data = blender_context.material.ms3d

        row = layout.row()
        row.prop(custom_data, 'name')

        col = layout.column()
        row = col.row()
        row.prop(custom_data, 'diffuse')
        row.prop(custom_data, 'ambient')
        row = col.row()
        row.prop(custom_data, 'specular')
        row.prop(custom_data, 'emissive')
        row = col.row()
        row.prop(custom_data, 'shininess')
        row.prop(custom_data, 'transparency')

        col = layout.column()
        row = col.row()
        row.prop(custom_data, 'texture')
        row = col.row()
        row.prop(custom_data, 'alphamap')
        row = col.row()
        row.prop(custom_data, 'mode', expand=True)

        row = layout.row()
        row.prop(custom_data, 'comment')

        #op = layout.row().operator(
        #        Ms3dUi.OPT_MATERIAL_APPLY,
        #        text=ms3d_str['ENUM_FROM_BLENDER_1'],
        #        icon='APPEND_BLEND')
        #if op:
        #    op.mode = 'FROM_BLENDER'
        pass

class BONE_PT_ms3d_bone(Panel):
    bl_label = ms3d_str['LABEL_PANEL_JOINTS']
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'bone'
    bl_order = 101

    @classmethod
    def poll(cls, blender_context):
        return (blender_context
                and blender_context.object.type in {'ARMATURE', }
                and blender_context.active_bone
                and isinstance(blender_context.active_bone, Bone)
                and blender_context.active_bone.ms3d is not None
                )

    def draw_header(self, _blender_context):
        layout = self.layout
        layout.label(icon='PLUGIN')

    def draw(self, blender_context):
        layout = self.layout
        custom_data = blender_context.active_bone.ms3d

        row = layout.row()
        row.prop(custom_data, 'name')
        row = layout.row()
        row.prop(custom_data, 'flags', expand=True)
        row = layout.row()
        row.prop(custom_data, 'color')
        row = layout.row()
        row.prop(custom_data, 'comment')

class DATA_PT_ms3d_group(Panel):
    bl_label = ms3d_str['LABEL_PANEL_GROUPS']
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'data'
    bl_order = 101

    @classmethod
    def poll(cls, blender_context):
        return (blender_context
                and blender_context.object
                and blender_context.object.type in {'MESH', }
                and blender_context.object.data
                and blender_context.object.data.ms3d is not None
                )

    def draw_header(self, _blender_context):
        layout = self.layout
        layout.label(icon='PLUGIN')

    def draw(self, blender_context):
        layout = self.layout
        custom_data = blender_context.object.data.ms3d
        layout.enabled = (blender_context.mode == 'EDIT_MESH') and (
                blender_context.tool_settings.mesh_select_mode[2])

        row = layout.row()

        row.template_list(
                listtype_name='DATA_UL_ms3d_group',
                list_id='',
                dataptr=custom_data,
                propname='groups',
                active_dataptr=custom_data,
                active_propname='selected_group_index',
                rows=2,
                type='DEFAULT',
                )

        col = row.column(align=True)
        col.operator(
                Ms3dUi.OPT_GROUP_APPLY,
                text="", icon='ADD').mode = 'ADD_GROUP'
        col.operator(
                Ms3dUi.OPT_GROUP_APPLY,
                text="", icon='REMOVE').mode = 'REMOVE_GROUP'

        index = custom_data.selected_group_index
        collection = custom_data.groups
        if (index >= 0 and index < len(collection)):
            row = layout.row()
            subrow = row.row(align=True)
            subrow.operator(
                    Ms3dUi.OPT_GROUP_APPLY,
                    text=ms3d_str['ENUM_ASSIGN_1']).mode = 'ASSIGN'
            subrow.operator(
                    Ms3dUi.OPT_GROUP_APPLY,
                    text=ms3d_str['ENUM_REMOVE_1']).mode = 'REMOVE'
            subrow = row.row(align=True)
            subrow.operator(
                    Ms3dUi.OPT_GROUP_APPLY,
                    text=ms3d_str['ENUM_SELECT_1']).mode = 'SELECT'
            subrow.operator(
                    Ms3dUi.OPT_GROUP_APPLY,
                    text=ms3d_str['ENUM_DESELECT_1']).mode = 'DESELECT'

            row = layout.row()
            row.prop(collection[index], 'flags', expand=True)

            row = layout.row()
            row.prop(collection[index], 'comment')

class DATA_PT_ms3d_smoothing_group(Panel):
    bl_label = ms3d_str['BL_LABEL_PANEL_SMOOTHING_GROUP']
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'data'
    bl_order = 102

    def preview(self, dict, id, text):
        item = dict.get(id)
        if item is None:
            return "{}".format(text)
        elif item:
            return "{}:".format(text)

        return "{}.".format(text)

    def build_preview(self, blender_context):
        dict = {}
        if (blender_context.mode != 'EDIT_MESH') or (
                not blender_context.tool_settings.mesh_select_mode[2]):
            return dict

        custom_data = blender_context.object.data.ms3d
        blender_mesh = blender_context.object.data
        bm = from_edit_mesh(blender_mesh)
        layer_smoothing_group = bm.faces.layers.int.get(
                ms3d_str['OBJECT_LAYER_SMOOTHING_GROUP'])
        if layer_smoothing_group is not None:
            for bmf in bm.faces:
                item = dict.get(bmf[layer_smoothing_group])
                if item is None:
                    dict[bmf[layer_smoothing_group]] = bmf.select
                else:
                    if not item:
                        dict[bmf[layer_smoothing_group]] = bmf.select
        return dict

    @classmethod
    def poll(cls, blender_context):
        return (blender_context
                and blender_context.object
                and blender_context.object.type in {'MESH', }
                and blender_context.object.data
                and blender_context.object.data.ms3d is not None
                )

    def draw_header(self, _blender_context):
        layout = self.layout
        layout.label(icon='PLUGIN')

    def draw(self, blender_context):
        dict = self.build_preview(blender_context)

        custom_data = blender_context.object.data.ms3d
        layout = self.layout
        layout.enabled = (blender_context.mode == 'EDIT_MESH') and (
                blender_context.tool_settings.mesh_select_mode[2])

        row = layout.row()
        subrow = row.row()
        subrow.prop(custom_data, 'apply_mode', expand=True)

        col = layout.column(align=True)
        subrow = col.row(align=True)
        subrow.operator(
                Ms3dUi.OPT_SMOOTHING_GROUP_APPLY,
                text=self.preview(dict, 1, "1")
                ).smoothing_group_index = 1
        subrow.operator(
                Ms3dUi.OPT_SMOOTHING_GROUP_APPLY,
                text=self.preview(dict, 2, "2")
                ).smoothing_group_index = 2
        subrow.operator(
                Ms3dUi.OPT_SMOOTHING_GROUP_APPLY,
                text=self.preview(dict, 3, "3")
                ).smoothing_group_index = 3
        subrow.operator(
                Ms3dUi.OPT_SMOOTHING_GROUP_APPLY,
                text=self.preview(dict, 4, "4")
                ).smoothing_group_index = 4
        subrow.operator(
                Ms3dUi.OPT_SMOOTHING_GROUP_APPLY,
                text=self.preview(dict, 5, "5")
                ).smoothing_group_index = 5
        subrow.operator(
                Ms3dUi.OPT_SMOOTHING_GROUP_APPLY,
                text=self.preview(dict, 6, "6")
                ).smoothing_group_index = 6
        subrow.operator(
                Ms3dUi.OPT_SMOOTHING_GROUP_APPLY,
                text=self.preview(dict, 7, "7")
                ).smoothing_group_index = 7
        subrow.operator(
                Ms3dUi.OPT_SMOOTHING_GROUP_APPLY,
                text=self.preview(dict, 8, "8")
                ).smoothing_group_index = 8
        subrow = col.row(align=True)
        subrow.operator(
                Ms3dUi.OPT_SMOOTHING_GROUP_APPLY,
                text=self.preview(dict, 9, "9")
                ).smoothing_group_index = 9
        subrow.operator(
                Ms3dUi.OPT_SMOOTHING_GROUP_APPLY,
                text=self.preview(dict, 10, "10")
                ).smoothing_group_index = 10
        subrow.operator(
                Ms3dUi.OPT_SMOOTHING_GROUP_APPLY,
                text=self.preview(dict, 11, "11")
                ).smoothing_group_index = 11
        subrow.operator(
                Ms3dUi.OPT_SMOOTHING_GROUP_APPLY,
                text=self.preview(dict, 12, "12")
                ).smoothing_group_index = 12
        subrow.operator(
                Ms3dUi.OPT_SMOOTHING_GROUP_APPLY,
                text=self.preview(dict, 13, "13")
                ).smoothing_group_index = 13
        subrow.operator(
                Ms3dUi.OPT_SMOOTHING_GROUP_APPLY,
                text=self.preview(dict, 14, "14")
                ).smoothing_group_index = 14
        subrow.operator(
                Ms3dUi.OPT_SMOOTHING_GROUP_APPLY,
                text=self.preview(dict, 15, "15")
                ).smoothing_group_index = 15
        subrow.operator(
                Ms3dUi.OPT_SMOOTHING_GROUP_APPLY,
                text=self.preview(dict, 16, "16")
                ).smoothing_group_index = 16
        subrow = col.row(align=True)
        subrow.operator(
                Ms3dUi.OPT_SMOOTHING_GROUP_APPLY,
                text=self.preview(dict, 17, "17")
                ).smoothing_group_index = 17
        subrow.operator(
                Ms3dUi.OPT_SMOOTHING_GROUP_APPLY,
                text=self.preview(dict, 18, "18")
                ).smoothing_group_index = 18
        subrow.operator(
                Ms3dUi.OPT_SMOOTHING_GROUP_APPLY,
                text=self.preview(dict, 19, "19")
                ).smoothing_group_index = 19
        subrow.operator(
                Ms3dUi.OPT_SMOOTHING_GROUP_APPLY,
                text=self.preview(dict, 20, "20")
                ).smoothing_group_index = 20
        subrow.operator(
                Ms3dUi.OPT_SMOOTHING_GROUP_APPLY,
                text=self.preview(dict, 21, "21")
                ).smoothing_group_index = 21
        subrow.operator(
                Ms3dUi.OPT_SMOOTHING_GROUP_APPLY,
                text=self.preview(dict, 22, "22")
                ).smoothing_group_index = 22
        subrow.operator(
                Ms3dUi.OPT_SMOOTHING_GROUP_APPLY,
                text=self.preview(dict, 23, "23")
                ).smoothing_group_index = 23
        subrow.operator(
                Ms3dUi.OPT_SMOOTHING_GROUP_APPLY,
                text=self.preview(dict, 24, "24")
                ).smoothing_group_index = 24
        subrow = col.row(align=True)
        subrow.operator(
                Ms3dUi.OPT_SMOOTHING_GROUP_APPLY,
                text=self.preview(dict, 25, "25")
                ).smoothing_group_index = 25
        subrow.operator(
                Ms3dUi.OPT_SMOOTHING_GROUP_APPLY,
                text=self.preview(dict, 26, "26")
                ).smoothing_group_index = 26
        subrow.operator(
                Ms3dUi.OPT_SMOOTHING_GROUP_APPLY,
                text=self.preview(dict, 27, "27")
                ).smoothing_group_index = 27
        subrow.operator(
                Ms3dUi.OPT_SMOOTHING_GROUP_APPLY,
                text=self.preview(dict, 28, "28")
                ).smoothing_group_index = 28
        subrow.operator(
                Ms3dUi.OPT_SMOOTHING_GROUP_APPLY,
                text=self.preview(dict, 29, "29")
                ).smoothing_group_index = 29
        subrow.operator(
                Ms3dUi.OPT_SMOOTHING_GROUP_APPLY,
                text=self.preview(dict, 30, "30")
                ).smoothing_group_index = 30
        subrow.operator(
                Ms3dUi.OPT_SMOOTHING_GROUP_APPLY,
                text=self.preview(dict, 31, "31")
                ).smoothing_group_index = 31
        subrow.operator(
                Ms3dUi.OPT_SMOOTHING_GROUP_APPLY,
                text=self.preview(dict, 32, "32")
                ).smoothing_group_index = 32
        subrow = col.row()
        subrow.operator(
                Ms3dUi.OPT_SMOOTHING_GROUP_APPLY,
                text=self.preview(dict, 0, ms3d_str['LABEL_PANEL_BUTTON_NONE'])
                ).smoothing_group_index = 0


###############################################################################
class IMPORT_OT_ms3d(Operator, ImportHelper):
    """ Load a MilkShape3D MS3D File """
    bl_idname = 'import_scene.ms3d'
    bl_label = ms3d_str['BL_LABEL_IMPORTER']
    bl_description = ms3d_str['BL_DESCRIPTION_IMPORTER']
    bl_options = {'PRESET', }
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'

    filename_ext: StringProperty(
            default=ms3d_str['FILE_EXT'],
            options={'HIDDEN', }
            )

    filter_glob: StringProperty(
            default=ms3d_str['FILE_FILTER'],
            options={'HIDDEN', }
            )

    verbose: EnumProperty(
            name=ms3d_str['PROP_NAME_VERBOSE'],
            description=ms3d_str['PROP_DESC_VERBOSE'],
            items=( (Ms3dUi.VERBOSE_MODE_NONE,
                            ms3d_str['ENUM_VERBOSE_NONE_1'],
                            ms3d_str['ENUM_VERBOSE_NONE_2'],
                            ),
                    (Ms3dUi.VERBOSE_MODE_NORMAL,
                            ms3d_str['ENUM_VERBOSE_NORMAL_1'],
                            ms3d_str['ENUM_VERBOSE_NORMAL_2'],
                            ),
                    (Ms3dUi.VERBOSE_MODE_MAXIMAL,
                            ms3d_str['ENUM_VERBOSE_MAXIMALIMAL_1'],
                            ms3d_str['ENUM_VERBOSE_MAXIMALIMAL_2'],
                            ),
                    ),
            default=Ms3dUi.PROP_DEFAULT_VERBOSE,
            )

    use_animation: BoolProperty(
            name=ms3d_str['PROP_NAME_USE_ANIMATION'],
            description=ms3d_str['PROP_DESC_USE_ANIMATION'],
            default=Ms3dUi.PROP_DEFAULT_USE_ANIMATION,
            )

    rotation_mode: EnumProperty(
            name=ms3d_str['PROP_NAME_ROTATION_MODE'],
            description=ms3d_str['PROP_DESC_ROTATION_MODE'],
            items=( (Ms3dUi.PROP_ITEM_ROTATION_MODE_EULER,
                            ms3d_str['PROP_ITEM_ROTATION_MODE_EULER_1'],
                            ms3d_str['PROP_ITEM_ROTATION_MODE_EULER_2']),
                    (Ms3dUi.PROP_ITEM_ROTATION_MODE_QUATERNION,
                            ms3d_str['PROP_ITEM_ROTATION_MODE_QUATERNION_1'],
                            ms3d_str['PROP_ITEM_ROTATION_MODE_QUATERNION_2']),
                    ),
            default=Ms3dUi.PROP_DEFAULT_ANIMATION_ROTATION,
            )

    use_joint_size: BoolProperty(
            name=ms3d_str['PROP_NAME_USE_JOINT_SIZE'],
            description=ms3d_str['PROP_DESC_USE_JOINT_SIZE'],
            default=Ms3dUi.PROP_DEFAULT_USE_JOINT_SIZE,
            )

    joint_size: FloatProperty(
            name=ms3d_str['PROP_NAME_IMPORT_JOINT_SIZE'],
            description=ms3d_str['PROP_DESC_IMPORT_JOINT_SIZE'],
            min=Ms3dUi.PROP_JOINT_SIZE_MIN, max=Ms3dUi.PROP_JOINT_SIZE_MAX,
            precision=Ms3dUi.PROP_JOINT_SIZE_PRECISION, \
                    step=Ms3dUi.PROP_JOINT_SIZE_STEP,
            default=Ms3dUi.PROP_DEFAULT_JOINT_SIZE,
            subtype='FACTOR',
            #options={'HIDDEN', },
            )

    use_joint_to_bones: BoolProperty(
            name=ms3d_str['PROP_NAME_JOINT_TO_BONES'],
            description=ms3d_str['PROP_DESC_JOINT_TO_BONES'],
            default=Ms3dUi.PROP_DEFAULT_JOINT_TO_BONES,
            )

    use_extended_normal_handling: BoolProperty(
            name=ms3d_str['PROP_NAME_EXTENDED_NORMAL_HANDLING'],
            description=ms3d_str['PROP_DESC_EXTENDED_NORMAL_HANDLING'],
            default=Ms3dUi.PROP_DEFAULT_EXTENDED_NORMAL_HANDLING,
            )


    @property
    def use_euler_rotation(self):
        return (Ms3dUi.PROP_ITEM_ROTATION_MODE_EULER \
                in self.rotation_mode)

    @property
    def use_quaternion_rotation(self):
        return (Ms3dUi.PROP_ITEM_ROTATION_MODE_QUATERNION \
                in self.rotation_mode)


    # draw the option panel
    def draw(_self, _blender_context):
        pass # rendered by MS3D_PT_import_p... operator.bl_idname == "IMPORT_SCENE_OT_ms3d"


    # entrypoint for MS3D -> blender
    def execute(self, blender_context):
        """ start executing """
        from .ms3d_import import (
                Ms3dImporter,
                )
        finished = Ms3dImporter(
                report=self.report,
                verbose=self.verbose,
                use_extended_normal_handling=self.use_extended_normal_handling,
                use_animation=self.use_animation,
                use_quaternion_rotation=self.use_quaternion_rotation,
                use_joint_size=self.use_joint_size,
                joint_size=self.joint_size,
                use_joint_to_bones=self.use_joint_to_bones,
                ).read(
                        blender_context,
                        self.filepath
                        )
        if finished:
            return {"FINISHED"}
        return {"CANCELLED"}

    @staticmethod
    def menu_func(cls, _blender_context):
        cls.layout.operator_context = 'INVOKE_DEFAULT'
        cls.layout.operator(
                IMPORT_OT_ms3d.bl_idname,
                text=ms3d_str['TEXT_OPERATOR'],
                )

class IMPORT_PT_ms3d_verbose(Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_parent_id = "FILE_PT_operator"
    bl_label = ms3d_str['LABEL_NAME_OPTIONS']
    bl_order = 101

    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator

        return operator.bl_idname == "IMPORT_SCENE_OT_ms3d"

    def draw_header(self, _blender_context):
        layout = self.layout
        layout.label(icon=Ms3dUi.ICON_OPTIONS)

    def draw(self, blender_context):
        sfile = blender_context.space_data
        operator = sfile.active_operator

        layout = self.layout
        box = layout.box()
        box.prop(operator, 'verbose', icon=Ms3dUi.ICON_VERBOSE)

class IMPORT_PT_ms3d_processing(Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_parent_id = "FILE_PT_operator"
    bl_label = ms3d_str['LABEL_NAME_PROCESSING']
    bl_order = 102

    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator

        return operator.bl_idname == "IMPORT_SCENE_OT_ms3d"

    def draw_header(self, _blender_context):
        layout = self.layout
        layout.label(icon=Ms3dUi.ICON_PROCESSING)

    def draw(self, blender_context):
        sfile = blender_context.space_data
        operator = sfile.active_operator

        layout = self.layout
        box = layout.box()
        box.prop(operator, 'use_extended_normal_handling')

class IMPORT_PT_ms3d_animation(Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_parent_id = "FILE_PT_operator"
    bl_label = ms3d_str['LABEL_NAME_ANIMATION']
    bl_order = 103

    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator

        return operator.bl_idname == "IMPORT_SCENE_OT_ms3d"

    def draw_header(self, _blender_context):
        layout = self.layout
        layout.label(icon=Ms3dUi.ICON_ANIMATION)

    def draw(self, blender_context):
        sfile = blender_context.space_data
        operator = sfile.active_operator

        layout = self.layout
        box = layout.box()
        box.prop(operator, 'use_animation')
        if (operator.use_animation):
            box.prop(operator, 'rotation_mode', icon=Ms3dUi.ICON_ROTATION_MODE,
                    expand=False)
            flow = box.column_flow()
            flow.prop(operator, 'use_joint_size')
            if (operator.use_joint_size):
                flow.prop(operator, 'joint_size')
            box.prop(operator, 'use_joint_to_bones')
            if (operator.use_joint_to_bones):
                box.box().label(text=ms3d_str['LABEL_NAME_JOINT_TO_BONES'],
                        icon=Ms3dUi.ICON_ERROR)


###############################################################################
class EXPORT_OT_ms3d(Operator, ExportHelper):
    """Save a MilkShape3D MS3D File"""
    bl_idname = 'export_scene.ms3d'
    bl_label = ms3d_str['BL_LABEL_EXPORTER']
    bl_description = ms3d_str['BL_DESCRIPTION_EXPORTER']
    bl_options = {'PRESET', }
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'

    filename_ext: StringProperty(
            default=ms3d_str['FILE_EXT'],
            options={'HIDDEN', }
            )

    filter_glob: StringProperty(
            default=ms3d_str['FILE_FILTER'],
            options={'HIDDEN', }
            )

    verbose: EnumProperty(
            name=ms3d_str['PROP_NAME_VERBOSE'],
            description=ms3d_str['PROP_DESC_VERBOSE'],
            items=( (Ms3dUi.VERBOSE_MODE_NONE,
                            ms3d_str['ENUM_VERBOSE_NONE_1'],
                            ms3d_str['ENUM_VERBOSE_NONE_2'],
                            ),
                    (Ms3dUi.VERBOSE_MODE_NORMAL,
                            ms3d_str['ENUM_VERBOSE_NORMAL_1'],
                            ms3d_str['ENUM_VERBOSE_NORMAL_2'],
                            ),
                    (Ms3dUi.VERBOSE_MODE_MAXIMAL,
                            ms3d_str['ENUM_VERBOSE_MAXIMALIMAL_1'],
                            ms3d_str['ENUM_VERBOSE_MAXIMALIMAL_2'],
                            ),
                    ),
            default=Ms3dUi.PROP_DEFAULT_VERBOSE,
            )

    use_blender_names: BoolProperty(
            name=ms3d_str['PROP_NAME_USE_BLENDER_NAMES'],
            description=ms3d_str['PROP_DESC_USE_BLENDER_NAMES'],
            default=Ms3dUi.PROP_DEFAULT_USE_BLENDER_NAMES,
            )

    use_blender_materials: BoolProperty(
            name=ms3d_str['PROP_NAME_USE_BLENDER_MATERIALS'],
            description=ms3d_str['PROP_DESC_USE_BLENDER_MATERIALS'],
            default=Ms3dUi.PROP_DEFAULT_USE_BLENDER_MATERIALS,
            )

    apply_transform: BoolProperty(
            name=ms3d_str['PROP_NAME_APPLY_TRANSFORM'],
            description=ms3d_str['PROP_DESC_APPLY_TRANSFORM'],
            default=Ms3dUi.PROP_DEFAULT_APPLY_TRANSFORM,
            )

    apply_modifiers: BoolProperty(
            name=ms3d_str['PROP_NAME_APPLY_MODIFIERS'],
            description=ms3d_str['PROP_DESC_APPLY_MODIFIERS'],
            default=Ms3dUi.PROP_DEFAULT_APPLY_MODIFIERS,
            )

    apply_modifiers_mode:  EnumProperty(
            name=ms3d_str['PROP_NAME_APPLY_MODIFIERS_MODE'],
            description=ms3d_str['PROP_DESC_APPLY_MODIFIERS_MODE'],
            items=( (Ms3dUi.PROP_ITEM_APPLY_MODIFIERS_MODE_VIEW,
                            ms3d_str['PROP_ITEM_APPLY_MODIFIERS_MODE_VIEW_1'],
                            ms3d_str['PROP_ITEM_APPLY_MODIFIERS_MODE_VIEW_2']),
                    (Ms3dUi.PROP_ITEM_APPLY_MODIFIERS_MODE_RENDER,
                            ms3d_str['PROP_ITEM_APPLY_MODIFIERS_MODE_RENDER_1'],
                            ms3d_str['PROP_ITEM_APPLY_MODIFIERS_MODE_RENDER_2']),
                    ),
            default=Ms3dUi.PROP_DEFAULT_APPLY_MODIFIERS_MODE,
            )

    use_animation: BoolProperty(
            name=ms3d_str['PROP_NAME_USE_ANIMATION'],
            description=ms3d_str['PROP_DESC_USE_ANIMATION'],
            default=Ms3dUi.PROP_DEFAULT_USE_ANIMATION,
            )

    normalize_weights: BoolProperty(
            name=ms3d_str['PROP_NAME_NORMALIZE_WEIGHTS'],
            description=ms3d_str['PROP_DESC_NORMALIZE_WEIGHTS'],
            default=Ms3dUi.PROP_DEFAULT_NORMALIZE_WEIGHTS,
            )

    shrink_to_keys: BoolProperty(
            name=ms3d_str['PROP_NAME_SHRINK_TO_KEYS'],
            description=ms3d_str['PROP_DESC_SHRINK_TO_KEYS'],
            default=Ms3dUi.PROP_DEFAULT_SHRINK_TO_KEYS,
            )

    bake_each_frame: BoolProperty(
            name=ms3d_str['PROP_NAME_BAKE_EACH_FRAME'],
            description=ms3d_str['PROP_DESC_BAKE_EACH_FRAME'],
            default=Ms3dUi.PROP_DEFAULT_BAKE_EACH_FRAME,
            )

    check_existing: BoolProperty(
            default=True,
            options={'HIDDEN', }
            )

    ##def object_items(self, blender_context):
    ##    return[(item.name, item.name, "") for item in blender_context.selected_objects if item.type in {'MESH', }]
    ##
    ##object_name: EnumProperty(
    ##        name="Object",
    ##        description="select an object to export",
    ##        items=object_items,
    ##        )

    ##EXPORT_ACTIVE_ONLY:
    ##limit availability to only active mesh object
    @classmethod
    def poll(cls, blender_context):
        return (blender_context
                and blender_context.active_object
                and blender_context.active_object.type in {'MESH', }
                and blender_context.active_object.data
                and blender_context.active_object.data.ms3d is not None
                )

    # draw the option panel
    def draw(_self, _blender_context):
        pass # rendered by MS3D_PT_export_p... operator.bl_idname == "EXPORT_SCENE_OT_ms3d"

    # entrypoint for blender -> MS3D
    def execute(self, blender_context):
        """start executing"""
        from .ms3d_export import (
                Ms3dExporter,
                )
        finished = Ms3dExporter(
                self.report,
                verbose=self.verbose,
                use_blender_names=self.use_blender_names,
                use_blender_materials=self.use_blender_materials,
                apply_transform=self.apply_transform,
                apply_modifiers=self.apply_modifiers,
                apply_modifiers_mode=self.apply_modifiers_mode,
                # TODO: export animation broken
                #use_animation=self.use_animation,
                use_animation=False,
                normalize_weights=self.normalize_weights,
                shrink_to_keys=self.shrink_to_keys,
                bake_each_frame=self.bake_each_frame,
                ).write(
                        blender_context,
                        self.filepath
                        )
        if finished:
            #blender_context.scene.update()
            return {"FINISHED"}
        return {"CANCELLED"}

    @staticmethod
    def menu_func(cls, blender_context):
        cls.layout.operator_context = 'INVOKE_DEFAULT'
        cls.layout.operator(
                EXPORT_OT_ms3d.bl_idname,
                text=ms3d_str['TEXT_OPERATOR']
                )

class EXPORT_PT_ms3d_verbose(Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_parent_id = "FILE_PT_operator"
    bl_label = ms3d_str['LABEL_NAME_OPTIONS']
    bl_order = 101

    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator

        return operator.bl_idname == "EXPORT_SCENE_OT_ms3d"

    def draw_header(self, _blender_context):
        layout = self.layout
        layout.label(icon=Ms3dUi.ICON_OPTIONS)

    def draw(self, blender_context):
        sfile = blender_context.space_data
        operator = sfile.active_operator

        layout = self.layout
        box = layout.box()
        flow = box.column_flow()
        flow.prop(operator, 'verbose', icon='SPEAKER')

class EXPORT_PT_ms3d_processing(Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_parent_id = "FILE_PT_operator"
    bl_label = ms3d_str['LABEL_NAME_PROCESSING']
    bl_order = 102

    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator
        return operator.bl_idname == "EXPORT_SCENE_OT_ms3d"

    def draw_header(self, _blender_context):
        layout = self.layout
        layout.label(icon=Ms3dUi.ICON_ACTIVE)

    def draw(self, blender_context):
        sfile = blender_context.space_data
        operator = sfile.active_operator

        layout = self.layout
        box = layout.box()
        flow = box.column_flow()
        row = flow.row()
        row.label(text=ms3d_str['PROP_NAME_ACTIVE'], icon=Ms3dUi.ICON_ACTIVE)
        row.label(text=blender_context.active_object.name)
        ##flow.prop(operator, 'object_name')
        flow.prop(operator, 'use_blender_names')
        #flow.prop(operator, 'use_blender_materials')

class EXPORT_PT_ms3d_modifier(Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_parent_id = "FILE_PT_operator"
    bl_label = ms3d_str['LABEL_NAME_MODIFIER']
    bl_order = 103

    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator
        return operator.bl_idname == "EXPORT_SCENE_OT_ms3d"

    def draw_header(self, _blender_context):
        layout = self.layout
        layout.label(icon=Ms3dUi.ICON_MODIFIER)

    def draw(self, blender_context):
        sfile = blender_context.space_data
        operator = sfile.active_operator

        layout = self.layout
        box = layout.box()
        flow = box.column_flow()
        flow.prop(operator, 'apply_transform')
        row = flow.row()
        row.prop(operator, 'apply_modifiers')
        #sub = row.row()
        #sub.active = operator.apply_modifiers
        #sub.prop(operator, 'apply_modifiers_mode', text="")
        flow.label(text="TODO: export animation broken", icon=Ms3dUi.ICON_ERROR)

class EXPORT_PT_ms3d_animation(Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_parent_id = "FILE_PT_operator"
    bl_label = ms3d_str['LABEL_NAME_ANIMATION']
    bl_order = 104

    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator
        return operator.bl_idname == "EXPORT_SCENE_OT_ms3d"

    def draw_header(self, _blender_context):
        layout = self.layout
        layout.label(icon=Ms3dUi.ICON_ANIMATION)

    def draw(self, blender_context):
        sfile = blender_context.space_data
        operator = sfile.active_operator

        layout = self.layout
        box = layout.box()
        box.label(text="TODO: export animation broken", icon=Ms3dUi.ICON_ERROR)
        #flow = box.column_flow()
        #flow.prop(operator, 'use_animation')
        #if (operator.use_animation):
        #    flow.prop(operator, 'normalize_weights')
        #    flow.prop(operator, 'shrink_to_keys')
        #    flow.prop(operator, 'bake_each_frame')


###############################################################################
classes = (
    Ms3dArmatureProperties,
    Ms3dGroupProperties,
    Ms3dJointProperties,
    Ms3dMaterialProperties,
    Ms3dModelProperties,

    DATA_OT_ms3d_apply_group,
    DATA_OT_ms3d_apply_smoothing_group,
    MATERIAL_OT_ms3d_apply_material,

    DATA_UL_ms3d_group,

    BONE_PT_ms3d_bone,
    DATA_PT_ms3d_group,
    DATA_PT_ms3d_smoothing_group,
    MATERIAL_PT_ms3d_material,
    OBJECT_PT_ms3d_mesh,

    IMPORT_OT_ms3d,
    IMPORT_PT_ms3d_verbose,
    IMPORT_PT_ms3d_processing,
    IMPORT_PT_ms3d_animation,

    EXPORT_OT_ms3d,
    EXPORT_PT_ms3d_verbose,
    EXPORT_PT_ms3d_processing,
    EXPORT_PT_ms3d_modifier,
    EXPORT_PT_ms3d_animation,
)

def register():
    for cls in classes:
        register_class(cls)
    inject_properties()
    TOPBAR_MT_file_import.append(IMPORT_OT_ms3d.menu_func)
    TOPBAR_MT_file_export.append(EXPORT_OT_ms3d.menu_func)

def unregister():
    TOPBAR_MT_file_import.remove(IMPORT_OT_ms3d.menu_func)
    TOPBAR_MT_file_export.remove(EXPORT_OT_ms3d.menu_func)
    delete_properties()
    for cls in classes:
        unregister_class(cls)


def inject_properties():
    Action.ms3d = PointerProperty(type=Ms3dArmatureProperties)
    Armature.ms3d = PointerProperty(type=Ms3dArmatureProperties)
    Bone.ms3d = PointerProperty(type=Ms3dJointProperties)
    Collection.ms3d = PointerProperty(type=Ms3dGroupProperties)
    Material.ms3d = PointerProperty(type=Ms3dMaterialProperties)
    Mesh.ms3d = PointerProperty(type=Ms3dModelProperties)

def delete_properties():
    del Action.ms3d
    del Armature.ms3d
    del Bone.ms3d
    del Collection.ms3d
    del Material.ms3d
    del Mesh.ms3d

###############################################################################


###############################################################################
#234567890123456789012345678901234567890123456789012345678901234567890123456789
#--------1---------2---------3---------4---------5---------6---------7---------
# ##### END OF FILE #####
