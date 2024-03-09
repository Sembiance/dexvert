# SPDX-License-Identifier: GPL-2.0-or-later
# Copyright (c)2011-2022 Alexander Nussbaumer

# <pep8 compliant>

bl_info = {
    "name": "MilkShape3D MS3D format (.ms3d)",
    "description": "Import-Export MilkShape3D MS3D files "
                   "(conform with MilkShape3D v1.8.4)",
    "author": "Alexander Nussbaumer",
    "version": (3, 2, 0),
    "blender": (3, 2, 0),
    "location": "File > Import-Export",
    "warning": "TODO: export animation broken",
    "doc_url": "{BLENDER_MANUAL_URL}/addons/import_export/scene_ms3d.html",
    "category": "Import-Export",
}


###############################################################################
#234567890123456789012345678901234567890123456789012345678901234567890123456789
#--------1---------2---------3---------4---------5---------6---------7---------


# To support reload properly, try to access a package var,
# if it's there, reload everything
if 'bpy' in locals():
    import importlib
    if 'ms3d_ui' in locals():
        importlib.reload(ms3d_ui)
else:
    from . import ms3d_ui



###############################################################################
# registration
def register():
    ms3d_ui.register()


def unregister():
    ms3d_ui.unregister()


###############################################################################
# global entry point
if (__name__ == "__main__"):
    register()


###############################################################################
#234567890123456789012345678901234567890123456789012345678901234567890123456789
#--------1---------2---------3---------4---------5---------6---------7---------
# ##### END OF FILE #####
