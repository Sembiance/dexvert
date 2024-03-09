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

import os
import struct

import bpy
import csv
import mathutils
import re
import shlex
from mathutils import Vector, Euler
from math import radians
from bpy import *
from bpy_extras.image_utils import load_image
from bpy_extras.io_utils import unpack_list, unpack_face_list
from bpy_extras.mesh_utils import ngon_tessellate

"""
This file is a reboot of the AC3D import script that is used to import .ac
format file into blender.

The original work carried out by Willian P Gerano was used to learn Python
and Blender, but inherent issues and a desire to do better has prompted a
complete re-write

Reference to the .ac format is found here:
http://www.inivis.com/ac3d/man/ac3dfileformat.html

Some noted points that are important for consideration:
 - AC3D appears to use Left-Handed axes, but with Y oriented "Up". Blender
   uses Right-Handed axes, the import does provide a rotation matrix applied
   to the world object that corrects this, so "Up" in the AC file appears as
   "Up" in blender - it's configurable, so you can change how it rotates...
 - AC3D supports only one texture per surface. This is a UV texture map, so
   it's imported as such in blender
 - Blender's Materials can have multiple textures per material - so a
   material + texure in AC3D requires a distinct and unique material in
   blender (more of an issue for the export routine)
 - AC3D supports individual face twosidedness, blender's twosidedness is
   per-object
TODO: Add setting so that .AC file is brought in relative to the 3D cursor

"""

DEBUG = False


def TRACE(message):
    if DEBUG:
        print(message)


class AcMat:
    """Container class that defines the material properties."""

    def __init__(self, name, rgb, amb, emis, spec, shi, trans, import_config):
        if name == "":
            name = "Default"
        self.name = re.sub('["]', '', name)  # string
        self.rgb = rgb				# [R,G,B]
        self.amb = amb				# [R,G,B]
        self.emis = emis			# [R,G,B]
        self.spec = spec			# [R,G,B]
        self.shi = shi				# integer
        self.trans = trans			# float

        self.rgba = [self.rgb[0], self.rgb[1], self.rgb[2], 1.0-self.trans]#used for non-nodes
        self.rgb4 = [self.rgb[0], self.rgb[1], self.rgb[2], 1.0]#used for nodes
        self.emis4 = [self.emis[0], self.emis[1], self.emis[2], 1.0]
        self.spec4 = [self.spec[0], self.spec[1], self.spec[2], 1.0]

        self.bmat_keys = {}			# dictionary list of blender materials
        self.bmat_keys.setdefault(None)
        self.bl_material = None		# untextured material
        self.import_config = import_config

    def make_blender_mat(self, bl_mat):
        # Blender:
        # ========
        # diffuse_intensity  : 0-1
        # diffuse_color      : 0-1 vector
        # mirror_color       : 0-1 vector
        # ambient            : 0-1
        # emit               : 0-2
        # specular_intensity : 0-1
        # specular_color     : 0-1 vector
        # specular_hardness  : 1-511
        # alpha              : 0-1
        #
        # AC3D:
        # ========
        # diffuse            : 0-1 vector
        # ambient            : 0-1 vector
        # emissive           : 0-1 vector
        # specular           : 0-1 vector
        # shininess          : 0-128
        # transparency       : 0-1
        #
        # bl_mat.specular_shader = 'PHONG' changed in 2.80

        

        # bl_mat.diffuse_intensity = 1.0 not supported by 2.80
        # bl_mat.ambient = \  not supported in 2.80
        #   (self.amb[0] + self.amb[1] + self.amb[2]) / 3.0
        # if self.import_config.use_amb_as_mircol:
        # 		bl_mat.mirror_color = self.amb
        # bl_mat.emit = \     not supported in 2.80
        #   ((self.emis[0] + self.emis[1] + self.emis[2]) / 3.0) * 2
        # if self.import_config.use_emis_as_mircol:
        # 		bl_mat.mirror_color = self.emis
        #bl_mat.specular_color = self.spec # although this can be set, it does not do anything, at least not with bsfd..
        

        
				
        acMin = 0.0
        acMax = 128.0
        blMin = 0.0
        blMax = 1.0

        acRange = (acMax - acMin)
        blRange = (blMax - blMin)
        rough = (((float(self.shi) - acMin) * blRange) / acRange) + blMin
        
        #bsdf.inputs['Roughness'].default_value = 1-rough
        
        # Set the basic non-nodes material properties
        bl_mat.roughness = 1-rough
        bl_mat.diffuse_color = self.rgba
        bl_mat.specular_intensity = sum(self.spec)/3.0
        
        if self.import_config.useEeveeSpecular:
            bl_mat.use_nodes = True
            bl_mat.node_tree.links.clear()
            bl_mat.node_tree.nodes.clear()
            bl_mat.use_nodes = True # It gets unset after clearing, so we set it again
        
            out = bl_mat.node_tree.nodes.new( type = 'ShaderNodeOutputMaterial' )
            speccy = bl_mat.node_tree.nodes.new( type = 'ShaderNodeEeveeSpecular' )#create new specular mat
        
            link   = bl_mat.node_tree.links.new(speccy.outputs['BSDF'], out.inputs['Surface'])#set that mat as default
        
            speccy.inputs['Emissive Color'].default_value = self.emis4
            speccy.inputs['Transparency'].default_value = self.trans
            speccy.inputs['Base Color'].default_value = self.rgb4
            speccy.inputs['Specular'].default_value = self.spec4
            speccy.inputs['Roughness'].default_value = 1-rough
        else:
            bl_mat.use_nodes = True
            bsdf = bl_mat.node_tree.nodes[bpy.app.translations.pgettext('Principled BSDF')]
            bsdf.inputs['Emission Color'].default_value = self.emis4
            bsdf.inputs['Alpha'].default_value = 1.0 - self.trans
            bsdf.inputs['Base Color'].default_value = self.rgb4
            bsdf.inputs['Specular IOR Level'].default_value = sum(self.spec)/3.0
            #bsdf.inputs['IOR'].default_value = 1.0
            #bsdf.inputs['Transmission'].default_value = 1.0
        
        return bl_mat

    """
    looks for a matching blender material (optionally with a texture),
    adds it when it doesn't exist
    """

    def get_blender_material(self, texrep, tex_name=''):
        bl_mat = None
        # tex_slot = None

        if tex_name == '':
            bl_mat = self.bl_material
            if bl_mat is None:
                bl_mat = bpy.data.materials.new(self.name)
                bl_mat = self.make_blender_mat(bl_mat)

                self.bl_material = bl_mat
        else:
            if (tex_name+str(texrep[0])+'-'+str(texrep[1])) in self.bmat_keys:
                bl_mat = self.bmat_keys[tex_name +
                                        str(texrep[0])+'-'+str(texrep[1])]
            else:
                bl_mat = bpy.data.materials.new(self.name)
                bl_mat = self.make_blender_mat(bl_mat)

                bsdf = None
                if self.import_config.useEeveeSpecular:
                    bsdf = bl_mat.node_tree.nodes[bpy.app.translations.pgettext("Specular")]
                else:
                    bsdf = bl_mat.node_tree.nodes[bpy.app.translations.pgettext("Principled BSDF")]
                    
                texImage = bl_mat.node_tree.nodes.new('ShaderNodeTexImage')
                texImage.image = self.get_blender_image(tex_name)
                bl_mat.node_tree.links.new(
                    bsdf.inputs['Base Color'], texImage.outputs['Color'])

                self.bmat_keys[tex_name +
                               str(texrep[0])+'-'+str(texrep[1])] = bl_mat

        return bl_mat

    """
    looks for the image in blender, adds it if it doesn't exist,
    returns the image to the callee
    """

    def get_blender_image(self, tex_name):
        bl_image = None

        if tex_name in bpy.data.images:
            return bpy.data.images[tex_name]

        found = False
        base_name = bpy.path.basename(tex_name)

        for path in [tex_name,
                     os.path.join(self.import_config.importdir, tex_name),
                     os.path.join(self.import_config.importdir, base_name)]:
            if os.path.exists(path):
                found = True

                try:
                    bl_image = bpy.data.images.load(
                        path, check_existing=True)
                except Exception:
                    if bl_image is None:
                        TRACE("Failed to load texture: "
                              "{0}".format(tex_name))

        if not found:
            TRACE("Failed to locate texture: {0}".format(tex_name))
            self.import_config.operator.report(
                {'WARNING'},
                'AC3D Importer: Failed to locate texture: "' +
                tex_name + '" in material "' + self.name + '".')

        return bl_image

    """
    looks for the blender texture, adds it if it doesn't exist
    """

    def get_blender_texture(self, tex_name, texrep):
        bl_tex = None
        # and bpy.data.textures[tex_name].repeat_x == texrep[0] and
        # bpy.data.textures[tex_name].repeat_y == texrep[1]:
        if tex_name in bpy.data.textures:
            bl_tex = bpy.data.textures[tex_name]
        else:
            bl_tex = bpy.data.textures.new(tex_name, 'IMAGE')
            bl_tex.image = self.get_blender_image(tex_name)
            bl_tex.use_preview_alpha = True

        return bl_tex


class AcObj:
    """Container class for a .ac OBJECT."""

    def __init__(self, ob_type, ac_file, import_config, world, parent=None):
        self.type = ob_type			# Type of object
        # reference to the parent object (if the object is World, then this
        # should be None)
        self.ac_parent = parent
        self.name = ''				# name of the object
        self.data = ''				# custom data
        self.tex_name = ''			# texture name (filename of texture)
        self.texrep = [1, 1]			# texture repeat
        self.texoff = [0, 0]			# texture offset
        self.subdiv = 0             # subdivision modifier
        # translation location of the center relative to the parent object
        self.location = [0, 0, 0]
        # 3x3 rotational matrix for vertices
        self.rotation = mathutils.Matrix(([1, 0, 0], [0, 1, 0], [0, 0, 1]))
        self.url = ''				# url of the object (??!)
        # crease angle for smoothing, 61 degs was chosen since that is what
        # OSG uses as default
        self.crease = 61
        self.use_crease = False     # if crease was specified in the AC3D file
        self.vert_list = []			# list of Vector(X,Y,Z) objects
        self.surf_list = []			# list of attached surfaces
        self.face_list = []			# flattened surface list
        self.surf_face_list = []    # list of surfs that is faces, no edges
        self.edge_list = []			# spare edge list (handles poly lines etc)
        self.face_mat_list = []		# flattened surface material index list
        self.children = []
        # Dictionary of ac_material index/texture pair to blender mesh
        # material index
        self.bl_mat_dict = {}
        self.world = world
        self.bl_obj = None			# Blender object
        self.import_config = import_config
        self.hidden = False

        self.tokens = {
            'numvert':	self.read_vertices,
            'numsurf':	self.read_surfaces,
            'name':		self.read_name,
            'data':		self.read_data,
            'kids':		self.read_children,
            'loc':		self.read_location,
            'rot':		self.read_rotation,
            'texture':	self.read_texture,
            'texrep':	self.read_texrep,
            'texoff':	self.read_texoff,
            'subdiv':	self.read_subdiv,
            'crease':	self.read_crease,
            'folded':	self.read_hierarchy_state,
            'locked':	self.read_hierarchy_state,
            'hidden':	self.read_hierarchy_state,
            'url':      self.read_url
        }

        self.read_ac_object(ac_file)

    """
    Read the object lines and dump them into this object, making hierarchial
    attachments to parents
    """

    def read_ac_object(self, ac_file):
        bDone = False
        while not bDone:
            line = self.world.readLine(ac_file)
            if line is None:
                break
            toks = shlex.split(line.strip())
            if len(toks) > 0:
                if toks[0] in self.tokens.keys():
                    bDone = self.tokens[toks[0]](ac_file, toks)
                else:
                    bDone = True

    def read_vertices(self, ac_file, toks):
        vertex_count = int(toks[1])
        for _n in range(vertex_count):
            line = self.world.readLine(ac_file)
            line = line.strip().split()
            if len(line) > 2:
                self.vert_list.append(Vector([float(x) for x in line]))
            else:
                self.readPrevious = True
                break

    def read_surfaces(self, ac_file, toks):
        surf_count = int(toks[1])

        for _n in range(surf_count):
            line = self.world.readLine(ac_file)
            if line is None:
                break
            line = line.strip().split()
            if line[0] == 'SURF':
                surf = AcSurf(line[1], ac_file, self.import_config, self.world)
                if(surf.flags.type != 0 or len(surf.refs) > 2):
                    self.surf_list.append(surf)
                else:
                    TRACE(
                        "Ignoring surface (vertex-count: {0})".format(
                            len(surf.refs)))

    def read_name(self, ac_file, toks):
        self.name = toks[1].strip('"')
        return False

    def read_data(self, ac_file, toks):
        line = self.world.readLine(ac_file)
        chars = int(toks[1])
        # Data can be multiline, so keep reading lines until all data is read,
        # but only use data in first line
        self.data = line[:chars]
        count = len(line)+1  # +1 is for newline char
        while (chars > count):
            count += len(self.world.readLine(ac_file))+1
        return False

    def read_hierarchy_state(self, ac_file, toks):
        # hidden: If an object should have restricted viewport visibility.
        # locked: Blender does not support locking of entire object.
        # folded: Blender API does not allow access to to this.
        # and self.import_config.hide_hidden_objects == True:
        if toks[0] == "hidden":
            self.hidden = True
        return False

    def read_url(self, ac_file, toks):
        # we read the url, but its not used for anything in Blender, since
        # Blender do not have that property.
        self.url = toks[1].strip('"')
        return False

    def read_location(self, ac_file, toks):
        self.location = (Vector([float(x) for x in toks[1:4]]))
        return False

    def read_rotation(self, ac_file, toks):
        temp = mathutils.Matrix(([float(x) for x in toks[1:4]], [float(
            x) for x in toks[4:7]], [float(x) for x in toks[7:10]]))
        rearranged = mathutils.Matrix().to_3x3()
        rearranged[0][0] = temp[0][0]
        rearranged[1][0] = temp[0][1]
        rearranged[2][0] = temp[0][2]
        rearranged[0][1] = temp[1][0]
        rearranged[1][1] = temp[1][1]
        rearranged[2][1] = temp[1][2]
        rearranged[0][2] = temp[2][0]
        rearranged[1][2] = temp[2][1]
        rearranged[2][2] = temp[2][2]
        self.rotation = rearranged
        return False

    def read_texture(self, ac_file, toks):
        self.tex_name = toks[1].strip('"')
        return False

    def read_texrep(self, ac_file, toks):
        self.texrep[0] = float(toks[1])
        self.texrep[1] = float(toks[2])
        return False

    def read_texoff(self, ac_file, toks):
        self.texoff = [float(toks[1]), float(toks[2])]
        return False

    def read_subdiv(self, ac_file, toks):
        self.subdiv = int(toks[1])
        return False

    def read_crease(self, ac_file, toks):
        self.crease = float(toks[1])
        self.use_crease = True
        return False

    def read_children(self, ac_file, toks):
        if self.type.lower() == 'world':
            # since children are always last thing read, we have to apply the
            # world rotation and location here, cause the global_matrix is
            # applied when making the children of world/scene.
            self4 = self.rotation.to_4x4()
            # self3 = mathutils.Matrix.Translation(self.location)
            self.import_config.global_matrix = \
                self4 @ self.import_config.global_matrix
            self.import_config.global_matrix[0][3] = self.location[0]
            self.import_config.global_matrix[1][3] = self.location[1]
            self.import_config.global_matrix[2][3] = self.location[2]

        num_kids = int(toks[1])
        for _n in range(num_kids):
            line = self.world.readLine(ac_file)
            if line is None:
                break
            line = line.strip().split()
            if len(line) > 1:
                self.children.append(
                    AcObj(line[1].strip('"'), ac_file,
                          self.import_config, self.world, self))
            else:
                self.readPrevious = True
                break
        # This is assumed to be the last thing in the list of things to read
        # returning True indicates to cease parsing this object
        return True

    """
    This function does the work of creating an object in Blender and
    configures it correctly
    """

    def create_blender_object(self, ac_matlist, str_pre,
                              bLevelLinked, mainSelf):
        me = None
        type_name = self.type.lower()

        if type_name == 'world':
            self.name = self.import_config.ac_name

        elif type_name == 'group':
            # Create an empty object
            bpy.ops.object.empty_add(type='PLAIN_AXES', radius=.01)
            self.bl_obj = bpy.context.active_object
            self.bl_obj.name = self.name

        elif type_name == 'poly':
            meshname = self.name + ".mesh"
            if len(self.data) > 0:
                meshname = self.data
            me = bpy.data.meshes.new(meshname)
            self.bl_obj = bpy.data.objects.new(self.name, me)

        elif type_name == 'light':
            # Create an light object
            lampname = self.name + ".lamp"
            if len(self.data) > 0:
                lampname = self.data

            lamp_data = bpy.data.lights.new(name=lampname, type='POINT')
            lamp_data.energy = 200

            self.bl_obj = bpy.data.objects.new(name=self.name,
                                               object_data=lamp_data)

        # setup parent object
        if self.bl_obj:
            if self.ac_parent and self.ac_parent.bl_obj:
                self.bl_obj.parent = self.ac_parent.bl_obj
            else:
                parentName = self.import_config.parent_to
                if parentName is not None and len(parentName) > 0:
                    parent_obj = bpy.data.objects[parentName]
                    if parent_obj is not None:
                        self.bl_obj.parent = parent_obj

        # make sure we have something to work with
        if self.vert_list and me:
            me.use_auto_smooth = self.use_crease
            me.auto_smooth_angle = radians(self.crease)
            two_sided_lighting = False
            has_uv = False

            for surf in self.surf_list:
                surf_edges = surf.get_edges()
                surf_face = surf.get_faces()

                for line in surf_edges:
                    self.edge_list.append(line)

                if surf.flags.type == 0:
                    # test for invalid face (ie, >4 vertices)
                    if len(surf.refs) < 3:
                        # not bringing in faces (assumed that there are none
                        # in a poly-line)
                        TRACE(
                            "Ignoring surface (vertex-count: {0})".format(
                                len(surf.refs)))
                    else:
                        # If one surface is twosided, they all will be...
                        two_sided_lighting |= surf.flags.two_sided

                        has_uv |= len(surf.uv_refs) > 0

                        self.face_list.append(surf_face)
                        self.surf_face_list.append(surf)

                        # Material index is 1-based, but the list we
                        # built is 0-based
                        ac_material = ac_matlist[surf.mat_index]
                        bl_material = ac_material.get_blender_material(
                            self.texrep, self.tex_name)

                        if bl_material is None:
                            TRACE("Error getting material {0} '{1}'".format(
                                surf.mat_index, self.tex_name))

                        fm_index = 0
                        if bl_material.name not in me.materials:
                            me.materials.append(bl_material)
                            fm_index = len(me.materials) - 1
                        else:
                            for mat in me.materials:
                                if mat == bl_material:
                                    break
                                fm_index += 1
                            if fm_index > len(me.materials):
                                TRACE("Failed to find material index")
                                fm_index = 0
                        self.face_mat_list.append(fm_index)
                else:
                    # treating as a polyline
                    two_sided_lighting |= surf.flags.two_sided

                    # Material index is 1 based, the list we built is 0 based
                    ac_material = ac_matlist[surf.mat_index]
                    bl_material = ac_material.get_blender_material(
                        self.texrep, self.tex_name)

                    if bl_material is None:
                        TRACE("Error getting material {0} '{1}'".format(
                            surf.mat_index, self.tex_name))

                    if bl_material.name not in me.materials:
                        # we here add the lines material to the object, but
                        # does never assign it to any edges.
                        # reason is edges cannot have material assigned.
                        # only reason we add it is in case the object only
                        # contains edges, so when exporting, that material
                        # (if there is only 1) will be assigned to every edge
                        # in the object.
                        me.materials.append(bl_material)

            # print(len(self.vert_list))
            me.from_pydata(self.vert_list, self.edge_list, self.face_list)

            # set smooth flag and apply material to each face
            for no, poly in enumerate(me.polygons):
                poly.material_index = self.face_mat_list[no]
                if self.surf_face_list[no].flags.shaded is True:
                    poly.use_smooth = True
                else:
                    poly.use_smooth = False

            # set smooth flag and apply material to each edge (disabled as
            # edges cannot be assigned material or smooth in Blender)
            if 1 == 0 and len(self.edge_list) > 0:
                # Standalone edges without faces.
                #
                # notice that an edge_key is actually a pair of indices
                # to vertices
                #
                faceEdgeKeys = set([])
                for poly in me.polygons:
                    for key in poly.edge_keys:
                        faceEdgeKeys.add(key)

                allEdgeKeys = set(me.edge_keys)
                freeEdgeKeys = allEdgeKeys.difference(faceEdgeKeys)
                # print(str(len(faceEdgeKeys)) + ' ' + \
                #     str(len(allEdgeKeys)) + ' ' + str(len(freeEdgeKeys)))

                freeEdges = set([])
                for f_edge in freeEdgeKeys:
                    for b_edge in me.edges:
                        if b_edge.key == f_edge:
                            freeEdges.add(b_edge)

                # for no, edge in enumerate(freeEdges):
                #    edge.material_index = self.line_mat_list[no]
                #    if self.surf_line_list[no].flags.shaded is True:
                #        edge.use_smooth = True
                #    else:
                #        edge.use_smooth = False

            # ensure a UV layer exists
            if me.uv_layers.active_index == -1:
                if len(me.uv_layers) == 0:
                    me.uv_layers.new(name="UVMap")
                if me.uv_layers.active_index == -1:
                    me.uv_layers[0].active = True

            uv_layer = me.uv_layers[me.uv_layers.active_index]

            me.update()

            # apply UV map
            uv_layer_index = 0
            for i, _face in enumerate(self.face_list):
                surf = self.surf_list[i]

                if len(self.tex_name) and len(surf.uv_refs) >= 3:
                    for _i_uv, uv in enumerate(surf.uv_refs):
                        uv_layer.data[uv_layer_index].uv = [uv[0]*self.texrep[0]+self.texoff[0], uv[1]*self.texrep[1]+self.texoff[1]]
                        uv_layer_index += 1

            #me.show_double_sided = two_sided_lighting#at least 1 face in this mesh is double sided, so we make whole mesh double sided.
            self.bl_obj.show_transparent = True

            # apply subdivision modifier
            if self.subdiv != 0:
                subName = self.name + ".subdiv"
                self.bl_obj.modifiers.new(name=subName, type='SUBSURF')

                modifier = self.bl_obj.modifiers[subName]
                modifier.levels = self.subdiv
                modifier.render_levels = self.subdiv

                # The below are default settings... uncomment to modify
                # modifier.subdivision_type = 'CATMULL_CLARK'
                # modifier.uv_smooth = 'NONE'

        if self.bl_obj:
            self3 = mathutils.Matrix.Translation(self.location)
            self4 = self.rotation.to_4x4()
            self.bl_obj.matrix_basis = self3 @ self4

            if self.ac_parent and self.ac_parent.type.lower() == 'world':
                matrix_basis = self.bl_obj.matrix_basis
                # order of this multiplication matters
                matrix_basis = self.import_config.global_matrix @ matrix_basis
                self.bl_obj.matrix_basis = matrix_basis

            if not self.ac_parent:
                # this is for the case where there is no world object
                matrix_basis = self.bl_obj.matrix_basis
                # order of this multiplication matters
                matrix_basis = self.import_config.global_matrix @ matrix_basis
                self.bl_obj.matrix_basis = matrix_basis

            coll_name = self.import_config.collection_name
            if not coll_name:
                coll_name = "Collection"

            scene_coll = self.import_config.context.scene.collection
            container = scene_coll.children.get(coll_name)
            if container is None:
                container = bpy.data.collections.new(coll_name)
                scene_coll.children.link(container)

            if not container.objects.get(self.bl_obj.name):
                container.objects.link(self.bl_obj)

            bpy.ops.object.select_all(action='DESELECT')
            self.bl_obj.select_set(True)
            # bpy.ops.object.origin_set('ORIGIN_GEOMETRY', 'MEDIAN')

            if self.hidden is True:
                self.bl_obj.hide_set(True)

        TRACE("{0}+-{1} ({2})".format(str_pre, self.name, self.data))

        # Add any children
        str_pre_new = ""
        bUseLink = True
        children = []
        for obj in self.children:
            if bLevelLinked:
                str_pre_new = str_pre + "| "
            else:
                str_pre_new = str_pre + "  "

            if self.children.index(obj) == len(self.children)-1:
                bUseLink = False

            child = obj.create_blender_object(
                ac_matlist, str_pre_new, bUseLink, mainSelf)
            if child and len(child) == 1:
                children.append(child[0])

        if me:
            # me.calc_normals()
            me.validate()
            me.update(calc_edges=True)

        if self.bl_obj:
            # return it so that if its top-level it can be selected.
            mainSelf.fullList.append(self.bl_obj)
            return [self.bl_obj]
        else:
            # if world then return all top level children:
            return children


class AcSurf:
    class AcSurfFlags:
        def __init__(self, flags):
            self.type = 0		# Surface Type: 0=Polygon, 1=closedLine, 2=Line
            self.shaded = False
            self.two_sided = False
            i = int(flags, 16)

            self.type = i & 0xF
            i = i >> 4
            if i & 1:
                self.shaded = True
            if i & 2:
                self.two_sided = True

    """
    Container class for surface definition within a parent object
    """

    def __init__(self, flags, ac_file, import_config, world):
        self.flags = self.AcSurfFlags(flags)    # surface flags
        self.mat_index = 0   # default material
        # list of indexes into the parent objects defined vertexes with
        # defined UV coordinates
        self.refs = []
        self.uv_refs = []
        self.tokens = {
            'mat':	self.read_surf_material,
            'refs':	self.read_surf_refs,
        }

        self.import_config = import_config
        self.world = world
        self.read_ac_surfaces(ac_file)

    def read_ac_surfaces(self, ac_file):
        surf_done = False
        while not surf_done:
            line = self.world.readLine(ac_file)
            if line is None:
                break
            toks = line.split()
            if len(toks) > 0:
                if toks[0] in self.tokens.keys():
                    surf_done = self.tokens[toks[0]](ac_file, toks)
                else:
                    surf_done = True

    def read_surf_material(self, ac_file, tokens):
        self.mat_index = int(tokens[1])
        return False

    def read_surf_refs(self, ac_file, tokens):
        num_refs = int(tokens[1])
        for _n in range(num_refs):
            line = self.world.readLine(ac_file)
            line = line.strip().split()

            self.refs.append(int(line[0]))
            self.uv_refs.append([float(x) for x in line[1:3]])
        return True

    def get_faces(self):
        # convert refs and surface type to faces
        surf_faces = []
        # make sure it's a face type polygon and that there's the right
        # number of vertices
        if self.flags.type == 0 and len(self.refs) > 2:
            surf_faces = self.refs
        return surf_faces

    def get_edges(self):
        # convert refs and surface type to edges
        surf_edges = []
        if self.flags.type != 0:
            # poly-line
            if len(self.refs) == 1:
                # Its not a line, but a point, so to get Blender to accept
                # that as a line we make that line have the vertex as both
                # the start and end point.
                mainline = []
                mainline.extend(self.refs)
                mainline.extend(self.refs)
                surf_edges.append(mainline)
            else:
                # its a line
                for i in range(0, len(self.refs)-1):
                    lineSegment = [self.refs[i], self.refs[i+1]]
                    surf_edges.append(lineSegment)
                if self.flags.type == 1 and len(self.refs) > 2:
                    # closed poly-line with more than 1 segment
                    surf_edges.append(
                        [self.refs[len(self.refs)-1], self.refs[0]])
        return surf_edges


class ImportConf:
    def __init__(
            self,
            operator,
            context,
            filepath,
            global_matrix,
            transparency_method,
            use_emis_as_mircol,
            use_amb_as_mircol,
            display_textured_solid,
            parent_to,
            collection_name,
            useEeveeSpecular):

        # Stuff that needs to be available to the working classes (ha!)
        self.operator = operator
        self.context = context
        self.global_matrix = global_matrix
#        self.use_transparency = use_transparency
        self.transparency_method = transparency_method
        self.use_emis_as_mircol = use_emis_as_mircol
        self.use_amb_as_mircol = use_amb_as_mircol
        self.display_textured_solid = display_textured_solid
#        self.hide_hidden_objects = hide_hidden_objects
        self.parent_to = parent_to
        self.collection_name = collection_name
        self.useEeveeSpecular = useEeveeSpecular

        # used to determine relative file paths
        self.importdir = os.path.dirname(filepath)
        self.ac_name = os.path.split(filepath)[1]
        TRACE("Importing {0}".format(self.ac_name))


class AC3D_OT_Import:
    def __init__(
            self,
            operator,
            context,
            filepath="",
            use_image_search=False,
            global_matrix=None,
            transparency_method='Z_TRANSPARENCY',
            use_emis_as_mircol=False,
            use_amb_as_mircol=False,
            display_textured_solid=False,
            parent_to="",
            collection_name="",
            useEeveeSpecular=False):

        self.import_config = ImportConf(
            operator,
            context,
            filepath,
            global_matrix,
            transparency_method,
            use_emis_as_mircol,
            use_amb_as_mircol,
            display_textured_solid,
            parent_to,
            collection_name,
            useEeveeSpecular)

        self.tokens = {
            'MATERIAL':		self.read_material,
            'MAT':			self.read_multiline_material,
            'OBJECT':		self.read_object,
        }
        self.oblist = []
        self.matlist = []

        # last read line of the file, stored incase we have to reread it,
        # due to bad AC file
        self.lastline = ''

        # should last line be reread instead of next line
        self.readPrevious = False

        self.line_num = 0

        operator.report(
            {'INFO'}, "Attempting import: {file}".format(file=filepath))

        # Check to make sure we're working with a valid AC3D file
        ac_file = open(filepath, 'r')

        condition = True
        while condition:
            self.header = ac_file.readline()
            if not self.header:
                self.header = ''
                break
            if self.header != '':
                condition = False

        self.header = self.header.strip()
        if len(self.header) != 5:
            operator.report(
                {'ERROR'},
                "Invalid file header length {0}: '{1}'".format(
                    len(self.header), self.header))
            ac_file.close()
            return None

        # pull out the AC3D file header
        AC3D_header = self.header[:4]
        AC3D_ver = self.header[4:5]
        if AC3D_header != 'AC3D':
            operator.report(
                {'ERROR'}, "Invalid file header: {0}".format(self.header))
            ac_file.close()
            return None

        if AC3D_ver == 'b':
            print("AC3D file is version 'b'")
        elif AC3D_ver == 'c':
            print("AC3D file is version 'c'")
        else:
            operator.report(
                {'ERROR'},
                "Unsupported AC3D version: {0}".format(self.header))
            ac_file.close()
            return None

        self.read_ac_file(ac_file)
        ac_file.close()

        self.create_blender_data()

        # Display as either textured solid (transparency only works in one
        # direction) or as textureless solids (transparency works)
        layout = bpy.data.screens['Layout']

        for bl_area in layout.areas:
            for bl_space in bl_area.spaces:
                if bl_space.type == 'VIEW_3D':
                    bl_space.overlay.show_relationship_lines = False
                    bl_space.shading.light = 'STUDIO'
                    bl_space.shading.color_type = 'TEXTURE'
                    bl_space.shading.background_type = 'THEME'
                    try:
                        bl_space.shading.studio_light = "outdoor.sl" # will gives exception sometimes when loading into a scene with prior models present
                    except:
                        print("Outdoor.sl failed to be applied")
                    # enable these 2 lines to use the scene lights to illuminate the scene in Dev Look
                    #bl_space.shading.use_scene_lights = True
                    #bl_space.shading.use_scene_World = True
                    break

        return None

    """
    Read a line from the AC file
    """

    def readLine(self, ac_file):
        if self.readPrevious:
            # print("Reading ", len(self.lastline), "prev:", self.lastline)
            self.readPrevious = False
            return self.lastline

        while True:
            # keep reading lines until we encounter a non-empty line
            line = ac_file.readline()
            self.line_num += 1

            if not line:
                # EOF, since there is no '\n'
                return None

            line = line.rstrip("\n").strip()
            if not line:
                # blank line, skip and read another line
                continue

            self.lastline = line
            # print("lastline=", self.lastline)

            return line

    """
    Simplifies the reporting of errors to the user
    """

    def report_error(self, message):
        TRACE(message)
        self.import_config.operator.report({'ERROR'}, message)

    """
    read our validated .ac file
    """

    def read_ac_file(self, ac_file):
        try:
            condition = True
            while condition:
                line = self.readLine(ac_file)
                if line is not None:
                    line = line.strip()
                    line = shlex.split(line)

                    # See if this is a valid token and pass the file handle
                    # and the current line to our function
                    if line[0] in self.tokens.keys():
                        self.tokens[line[0]](ac_file, line)
                    else:
                        self.report_error(
                            "invalid token: {tok} ({ln})".format(tok=line[0],
                                                                 ln=line))
                else:
                    condition = False
        except Exception as e:
            self.report_error('AC3D import error, line %d: %s' %
                              (self.line_num, e))

    """
    Take the passed in line and interpret as a .ac material
    """

    def read_material(self, ac_file, line):

        # MATERIAL %s rgb  %f %f %f  amb   %f %f %f
        #             emis %f %f %f  spec  %f %f %f
        #             shi  %d        trans %f
        self.matlist.append(
            AcMat(
                line[1],
                [float(x) for x in line[3:6]],
                [float(x) for x in line[7:10]],
                [float(x) for x in line[11:14]],
                [float(x) for x in line[15:18]],
                # it should be int but float seems to be used sometimes
                float(line[19]),
                float(line[21]),
                self.import_config))

    def read_mat_line(self, ac_file):
        line = self.readLine(ac_file)
        if line is not None:
            line = shlex.split(line)
        else:
            self.report_error("unexpected end of file in materials")
        return line

    """
    Process multiline material in AC3D file version 'c' (ver12)
    """

    def read_multiline_material(self, ac_file, line):
        # MAT %s
        # rgb %f %f %f
        # amb %f %f %f
        # emis %f %f %f
        # spec %f %f %f
        # shi %d
        # trans %f
        # data %d
        # dataContent
        # dataContent
        # ENDMAT
        if len(line) != 2:
            self.report_error(
                "invalid material name on line ({ln})".format(ln=line))
        name = line[1]
        line = self.read_mat_line(ac_file)
        if line[0] != 'rgb' or len(line) != 4:
            self.report_error(
                "invalid material rgb on line ({ln})".format(ln=line))
        rgb = [float(x) for x in line[1:4]]
        line = self.read_mat_line(ac_file)
        if line[0] != 'amb' or len(line) != 4:
            self.report_error(
                "invalid material amb on line ({ln})".format(ln=line))
        amb = [float(x) for x in line[1:4]]
        line = self.read_mat_line(ac_file)
        if line[0] != 'emis' or len(line) != 4:
            self.report_error(
                "invalid material emis on line ({ln})".format(ln=line))
        emis = [float(x) for x in line[1:4]]
        line = self.read_mat_line(ac_file)
        if line[0] != 'spec' or len(line) != 4:
            self.report_error(
                "invalid material spec on line ({ln})".format(ln=line))
        spec = [float(x) for x in line[1:4]]
        line = self.read_mat_line(ac_file)
        if line[0] != 'shi' or len(line) != 2:
            self.report_error(
                "invalid material shi on line ({ln})".format(ln=line))
        # it should be int but float seems to be used sometimes
        shi = float(line[1])
        line = self.read_mat_line(ac_file)
        if line[0] != 'trans' or len(line) != 2:
            self.report_error(
                "invalid material trans on line ({ln})".format(ln=line))
        trans = float(line[1])
        line = self.read_mat_line(ac_file)
        if line[0] == 'data':
            line = self.read_mat_line(ac_file)
            while line is not None and line[0] != 'ENDMAT':
                line = self.read_mat_line(ac_file)
        if line[0] != 'ENDMAT' or len(line) != 1:
            self.report_error(
                "invalid material ENDMAT on line ({ln})".format(ln=line))
        self.matlist.append(AcMat(name, rgb, amb, emis, spec,
                                  shi, trans, self.import_config))

    """
    Read the Object definition (including child objects)
    """

    def read_object(self, ac_file, line):
        # OBJECT %s
        self.oblist.append(AcObj(line[1], ac_file, self.import_config, self))

    """
    Reads the data imported from the file and creates blender data
    """

    def create_blender_data(self):

        self.fullList = []

        # go through the list of objects
        bUseLink = True
        top_level_objects = []
        for obj in self.oblist:
            if self.oblist.index(obj) == len(self.oblist)-1:
                bUseLink = False
            tlo = obj.create_blender_object(self.matlist, "", bUseLink, self)
            if len(tlo) > 0:
                for tloc in tlo:
                    top_level_objects.append(tloc)

        # only traverse what we import, not what is already in Blender
        for obj in self.fullList:
            if obj.matrix_basis.is_negative:
                # when negative scaling is applied, normals might be flipped,
                # so we apply the scaling in those cases.
                obj.select_set(True)
                bpy.context.scene.collection.objects.active = obj
                bpy.ops.object.transform_apply(
                    location=False, rotation=False, scale=True)

        for obj in bpy.data.objects:
            obj.select_set(False)
        for obj in top_level_objects:
            # imported top level objects will be selected
            obj.select_set(True)
