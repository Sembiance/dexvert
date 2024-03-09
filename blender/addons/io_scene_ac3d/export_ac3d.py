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

"""
This file is a complete reboot of the AC3D export script that is used to
export .ac format file from within Blender.

Reference to the .ac format is found here:
http://www.inivis.com/ac3d/man/ac3dfileformat.html

Some noted points that are important for consideration:
 - AC3D appears to use Left-Handed axes, but with Y oriented "Up".
   Blender uses Right-Handed axes, the export does provide a rotation matrix
   applied to the world object that corrects this, so "Up" in Blender
   becomes "Up" in the .AC file - it's configurable, so you can change how
   it rotates...
 - AC3D supports only one texture per surface. This is a UV texture map, so
   only Blender's texmap is exported
 - Blender's Materials can have multiple textures per material - so a
   material + texure in AC3D requires a distinct and unique material in
   blender. The export uses a comparison of material properties to see if a
   material is the same as another one and then uses that material index for
   the .ac file.

TODO: Option to define "DefaultWhite" material
TODO: Optionally over-write existing textures
"""

from . import AC3D

import os
import bpy
from math import radians
from mathutils import Matrix


def TRACE(message):
    AC3D.TRACE(message)


class ExportConf:
    def __init__(
        self,
        operator,
        context,
        filepath,
        global_matrix,
        export_rot,
        use_render_layers,
        use_selection,
        merge_materials,
        mircol_as_emis,
        mircol_as_amb,
        amb_as_diff,
        export_lines,
        export_hidden,
        export_lights,
        crease_angle,
        global_doublesided,
    ):
        # Stuff that needs to be available to the working classes (ha!)
        self.operator = operator
        self.context = context
        self.global_matrix = global_matrix
        self.use_selection = use_selection
        self.use_render_layers = use_render_layers
        self.mircol_as_emis = mircol_as_emis
        self.mircol_as_amb = mircol_as_amb
        self.amb_as_diff = amb_as_diff
        self.crease_angle = crease_angle
        self.merge_materials = merge_materials
        self.export_lines = export_lines
        self.export_hidden = export_hidden
        self.export_rot = export_rot
        self.export_lights = export_lights
        self.global_doublesided=global_doublesided
        # if any mesh has no material, this will be changed to 0 and
        # DefaultWhite will be output.
        self.mat_offset = 1

        # used to determine relative file paths
        self.exportdir = os.path.dirname(filepath)
        self.ac_name = os.path.split(filepath)[1]
        TRACE('Exporting to {0}'.format(self.ac_name))


class AC3D_OT_Export:
    def __init__(
        self,
        operator,
        context,
        filepath='',
        global_matrix=None,
        export_rot=False,
        use_render_layers=True,
        use_selection=False,
        merge_materials=False,
        mircol_as_emis=True,
        mircol_as_amb=False,
        amb_as_diff=False,
        export_lines=False,
        export_hidden=False,
        export_lights=False,
        crease_angle=radians(40.0),
        global_doublesided=False,
    ):

        self.export_conf = ExportConf(
            operator,
            context,
            filepath,
            global_matrix,
            export_rot,
            use_render_layers,
            use_selection,
            merge_materials,
            mircol_as_emis,
            mircol_as_amb,
            amb_as_diff,
            export_lines,
            export_hidden,
            export_lights,
            crease_angle,
            global_doublesided,
        )

        # TRACE("Global: {0}".format(global_matrix))

        self.ac_mats = [AC3D.Material('DefaultWhite', None, self.export_conf)]
        self.ac_world = None

        # Parsing the tree in a top down manner and check on the way down which
        # objects are to be exported

        self.world = AC3D.World(
            'Blender_exporter_v' + str(operator.v_info[0]) + "." +
            str(operator.v_info[1]) + "__" + bpy.path.basename(filepath),
            self.export_conf)
        self.parseLevel(
            self.world,
            [ob for ob in bpy.data.objects
             if ob.parent is None and not ob.library])
        self.world.parse(self.ac_mats)

        # dump the contents of the lists to file
        ac_file = open(filepath, 'w')
        ac_file.write('AC3Db\n')
        for ac_mat in self.ac_mats:
            ac_mat.write(ac_file)

        self.world.write(ac_file)
        ac_file.close()

    def parseLevel(self,
                   parent,
                   objects,
                   ignore_select=False,
                   local_transform=Matrix()):
        """
        Parse a level in the object hierarchy
        """
        for ob in objects:

            ac_ob = None

            # Objects from libraries don't have the select flag set even if
            # their proxy is selected. We therefore consider all objects from
            # libraries as selected, as the only possibility to get them
            # considered is if their proxy should be exported.
            hidden = ob.hide_get()
            if self.export_conf.export_hidden:
                ob.hide_set(False)

            if (not self.export_conf.use_render_layers or
                ob.visible_get()) and (#was .is_visible(self.export_conf.context.scene)
                (not self.export_conf.use_selection or
                 ob.select_get() or ignore_select)):
                ob.hide_set(hidden)

                # We need to check for dupligroups first as every type of
                # object can be converted to a dupligroup without removing
                # the data from the old type.
                if ob.instance_type == 'GROUP':#was .dupli_type
                    ac_ob = AC3D.Group(
                        ob.name, ob, self.export_conf, local_transform)
                    children = [
                        child for child in ob.dupli_group.objects
                        if not child.parent or
                        child.parent.name not in ob.dupli_group.objects]
                    self.parseLevel(ac_ob, children, True,
                                    local_transform @ ob.matrix_world)
                elif ob.type in ['MESH', 'LATTICE', 'SURFACE', 'CURVE']:
                    ac_ob = AC3D.Poly(
                        ob.name, ob, self.export_conf, local_transform)
                elif ob.type == 'ARMATURE':
                    p = parent
                    for bone in ob.pose.bones:
                        for c in ob.children:
                            if c.parent_bone == bone.name:
                                ac_child = AC3D.Poly(
                                    c.name, c,
                                    self.export_conf, local_transform)
                                p.addChild(ac_child)
                                p = ac_child

                                if len(c.children):
                                    self.parseLevel(
                                        p, c.children,
                                        ignore_select, local_transform)
                    continue
                elif ob.type == 'EMPTY':
                    ac_ob = AC3D.Group(
                        ob.name, ob, self.export_conf, local_transform)
                elif ob.type == 'LIGHT' and self.export_conf.export_lights:
                    ac_ob = AC3D.Light(
                        ob.name, ob, self.export_conf, local_transform)
                else:
                    TRACE('Skipping object {0} (type={1})'.format(
                        ob.name, ob.type))
            ob.hide_set(hidden)
            if ac_ob:
                parent.addChild(ac_ob)
                next_parent = ac_ob
            else:
                # if link chain is broken (aka one element not exported) the
                # object will be placed in global space (=world)
                next_parent = self.world

            if len(ob.children):
                self.parseLevel(next_parent, ob.children,
                                ignore_select, local_transform)
