import bpy

from struct import Struct
from collections import namedtuple
from io import BytesIO


def get_index_of_tuples(ts, index, default):
    return tuple(default if len(t) <= index else t[index] for t in ts)


def noop(value):
    return value


class AnyStruct:
    def __init__(self, name, fields):
        self.ntuple_cls = namedtuple(name, [f[0] for f in fields])
        self.struct = Struct('<' + ''.join([f[1] for f in fields]))
        self.tupling = get_index_of_tuples(fields, 2, 1)
        self.frombin = get_index_of_tuples(fields, 3, noop)
        self.tobin = get_index_of_tuples(fields, 4, noop)

    @property
    def size(self):
        return self.struct.size

    def unpack(self, bs):
        pt = self.struct.unpack(bs)
        t = []
        pti = iter(pt)
        for sz, conv_func in zip(self.tupling, self.frombin):
            if sz == 1:
                value = next(pti)
            else:
                value = tuple(next(pti) for i in range(sz))
            t.append(conv_func(value))
        return self.ntuple_cls._make(t)

    def funpack(self, f):
        return self.unpack(f.read(self.size))

    def pack(self, *a, **kw):
        t = self.ntuple_cls(*a, **kw)
        pt = []
        for value, sz, conv_func in zip(t, self.tupling, self.tobin):
            value = conv_func(value)
            if sz == 1:
                pt.append(value)
            else:
                assert len(value) == sz
                pt.extend(value)
        return self.struct.pack(*pt)

    def fpack(self, f, *a, **kw):
        return f.write(self.pack(*a, **kw))


class OffsetBytesIO:
    def __init__(self, start_offset=0):
        self.shift = start_offset
        self.file = BytesIO(b'')
        self.offsets = {}

    def mark(self, name):
        self.offsets[name] = self.file.tell() + self.shift

    def write(self, data):
        self.file.write(data)

    def getvalue(self):
        return self.file.getvalue()

    def getoffsets(self):
        return self.offsets.copy()


# =========================== #
# blender backward compatable
def get_preferences(context=None):
    ''' Multi version compatibility for getting preferences
    https://theduckcow.com/2019/update-addons-both-blender-28-and-27-support/#synved-sections-1-7
    '''
    if not context:
        context = bpy.context
    prefs = None
    if hasattr(context, "user_preferences"):
        prefs = context.user_preferences.addons.get(__package__, None)
    elif hasattr(context, "preferences"):
        prefs = context.preferences.addons.get(__package__, None)
    if prefs:
        return prefs.preferences
    else:
        raise Exception("Could not fetch user preferences")


def get_coll_group(context):
    if hasattr(context, "collection"):
        return context.collection  # B2.8
    else:
        return context.groups


def get_contex_obj(context):
    if hasattr(context, "collection"):
        return context.collection.objects  # B2.8
    else:
        return context.scene.objects


def get_objects(context):
    if hasattr(context, "view_layer"):
        return context.view_layer.objects  # B2.8
    else:
        return context.scene.objects


def get_layers(context):
    if hasattr(context, "view_layer"):
        return context.view_layer  # B2.8
    else:
        return context.scene


def get_menu_import():
    if hasattr(bpy.types, "TOPBAR_MT_file_import"):
        return bpy.types.TOPBAR_MT_file_import
    elif hasattr(bpy.types, "INFO_MT_file_import"):
        return bpy.types.INFO_MT_file_import
    else:
        raise Exception("Could not fetch menu")


def get_menu_export():
    if hasattr(bpy.types, "TOPBAR_MT_file_export"):
        return bpy.types.TOPBAR_MT_file_export
    elif hasattr(bpy.types, "INFO_MT_file_export"):
        return bpy.types.INFO_MT_file_export
    else:
        raise Exception("Could not fetch menu")


def get_groups():
    if hasattr(bpy.data, "collections"):
        mygroup = bpy.data.collections.get("MyGroup")
    else:
        mygroup = bpy.data.groups.get("MyGroup")


def get_uv_data_new(context, uv_name=""):
    ret = (0, None)
    if hasattr(context, "uv_textures"):
        # print("found uv_textures")
        ret = (1, context.uv_textures.new(name=uv_name))  # tessface_uv_textures
        context.uv_textures.active = ret[1]
    else:
        # print("found uv_layers")  # B2.8
        ret = (2, context.uv_layers.new(name=uv_name))
        context.uv_layers.active = ret[1]
    return ret


def get_uv_data(context):
    ret = (0, None)
    if hasattr(context, "uv_textures"):
        return context.uv_textures
    else:
        return context.uv_layers  # B2.8


def get_hide(context):
    if hasattr(context, "hide_viewport"):
        return context.hide_viewport  # B2.8
    else:
        return context.hide


def get_empty_draw_type(context):
    if hasattr(context, "empty_draw_type"):
        return context.empty_draw_type  # B3.0
    else:
        return context.empty_display_type


def set_empty_draw_type(context, type):
    if hasattr(context, "empty_draw_type"):
        context.empty_draw_type = type  # B3.0
    else:
        context.empty_display_type = type


def set_select_state(context, opt):
    """Multi version compatibility for setting object selection
    https://theduckcow.com/2019/update-addons-both-blender-28-and-27-support/#synved-sections-1-11
    """
    if hasattr(context, "select_set"):
        context.select_set(state=opt)  # B2.8
    else:
        context.select = opt


def set_mode_state(context, opt):
    """Multi version compatibility for setting object selection
    https://theduckcow.com/2019/update-addons-both-blender-28-and-27-support/#synved-sections-1-11
    """
    if hasattr(context, "mode_set"):
        context.mode_set(state=opt)  # B2.8
    else:
        context.mode = opt


def set_uv_array(context, index, x, y):
    return context


def set_uv_data_active(context, obj):
    if hasattr(context, "uv_layers"):
        context.uv_layers.active = obj
    else:
        context.tessface_uv_textures.active = obj


def make_annotations(cls):
    """Add annotation attribute to fields to avoid Blender 2.8+ warnings
    https://github.com/OpenNaja/cobra-tools/blob/master/addon_updater_ops.py"""
    if not hasattr(bpy.app, "version") or bpy.app.version < (2, 80):
        return cls
    if bpy.app.version < (2, 93, 0):
        bl_props = {k: v for k, v in cls.__dict__.items()
                    if isinstance(v, tuple)}
    else:
        bl_props = {k: v for k, v in cls.__dict__.items()
                    if isinstance(v, bpy.props._PropertyDeferred)}
    if bl_props:
        if '__annotations__' not in cls.__dict__:
            setattr(cls, '__annotations__', {})
        annotations = cls.__dict__['__annotations__']
        for k, v in bl_props.items():
            annotations[k] = v
            delattr(cls, k)
    return cls


def get_user_preferences(context=None):
    """Intermediate method for pre and post blender 2.8 grabbing preferences
    https://github.com/OpenNaja/cobra-tools/blob/master/addon_updater_ops.py"""
    if not context:
        context = bpy.context
    prefs = None
    if hasattr(context, "user_preferences"):
        prefs = context.user_preferences.addons.get(__package__, None)
    elif hasattr(context, "preferences"):
        prefs = context.preferences.addons.get(__package__, None)
    if prefs:
        return prefs.preferences
    # To make the addon stable and non-exception prone, return None
    # raise Exception("Could not fetch user preferences")
    return None
