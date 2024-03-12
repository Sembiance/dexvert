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

import bpy

# When bpy is already in local, we know this is not the initial import...
if "bpy" in locals():
    import importlib
    # ...so we need to reload our submodule(s) using importlib
    if "lxo_reader" in locals():
        importlib.reload(lxo_reader)

from . import lxo_reader
from mathutils import Matrix, Euler
from math import sqrt
import json


def create_light(lxo_item: lxo_reader.LXOItem, item_name: str, light_materials: dict[str, lxo_reader.LXOItem]):
    # specific light stuff first to get the data object
    object_data = None
    if lxo_item.typename == "areaLight":
        object_data = bpy.data.lights.new(item_name, 'AREA')
        object_data.shape = 'RECTANGLE'  # TODO: lxoItem.channel['shape']
        object_data.size = lxo_item.channel['width']
        object_data.size_y = lxo_item.channel['height']
        area = lxo_item.channel['width'] * lxo_item.channel['height']
        # doing some fancy math to convert modo radiance to blender power
        power = lxo_item.channel['radiance'] * (sqrt(area) * 2) ** 2
        object_data.energy = power
    elif lxo_item.typename == "spotLight":
        object_data = bpy.data.lights.new(item_name, 'SPOT')
        object_data.energy = lxo_item.channel['radiance']
    elif lxo_item.typename == "pointLight":
        object_data = bpy.data.lights.new(item_name, 'POINT')
        object_data.energy = lxo_item.channel['radiance']
    elif lxo_item.typename == "sunLight":
        object_data = bpy.data.lights.new(item_name, 'SUN')
        object_data.angle = lxo_item.channel['spread']
        object_data.energy = lxo_item.channel['radiance']

    # general light stuff
    if object_data is not None:
        light_material = light_materials[lxo_item.id]
        light_color = light_material.CHNV['lightCol']
        object_data.color = (light_color[0][1],
                             light_color[1][1],
                             light_color[2][1])

    return object_data


def create_uvmaps(lxo_layer: lxo_reader.LXOLayer, mesh: bpy.types.Mesh):
    allmaps = set(list(lxo_layer.uv_maps_disco.keys()))
    allmaps = sorted(allmaps.union(set(list(lxo_layer.uv_maps.keys()))))
    print(f"Adding {len(allmaps)} UV Textures")
    if len(allmaps) > 8:
        print(f"This mesh contains more than 8 UVMaps: {len(allmaps)}")

    for uvmap_key in allmaps:
        uvm = mesh.uv_layers.new()
        if uvm is None:
            break
        uvm.name = uvmap_key

    vertloops = {}
    for v in mesh.vertices:
        vertloops[v.index] = []
    for loop in mesh.loops:
        vertloops[loop.vertex_index].append(loop.index)
    for uvmap_key in lxo_layer.uv_maps.keys():
        uvcoords = lxo_layer.uv_maps[uvmap_key]
        uvm = mesh.uv_layers.get(uvmap_key)
        if uvm is None:
            continue
        for pnt_id, (u, v) in uvcoords.items():
            for li in vertloops[pnt_id]:
                uvm.data[li].uv = [u, v]
    for uvmap_key in lxo_layer.uv_maps_disco.keys():
        uvcoords = lxo_layer.uv_maps_disco[uvmap_key]
        uvm = mesh.uv_layers.get(uvmap_key)
        if uvm is None:
            continue
        for pol_id in uvcoords.keys():
            for pnt_id, (u, v) in uvcoords[pol_id].items():
                for li in mesh.polygons[pol_id].loop_indices:
                    if pnt_id == mesh.loops[li].vertex_index:
                        uvm.data[li].uv = [u, v]
                        break


def create_normals(lxo_layer: lxo_reader.LXOLayer, mesh: bpy.types.Mesh):
    # need to enable auto smooth first, otherwise loop normals aren't stored
    #mesh.use_auto_smooth = True

    allmaps = set(list(lxo_layer.vertex_normals_disco.keys()))
    allmaps = sorted(allmaps.union(set(list(lxo_layer.vertex_normals.keys()))))
    print(f"Adding vertex normals")
    # Modo support multiple vertex normal maps, we use the first,
    # then cover our eyes and pretend to not see anything
    for map_name in allmaps:
        # now cover your eyes
        break
    # all good, everything is fine, the world is still spinning, open your eyes

    vertloops = {}
    for v in mesh.vertices:
        vertloops[v.index] = []
    for loop in mesh.loops:
        vertloops[loop.vertex_index].append(loop.index)

    lxo_vertex_normals = lxo_layer.vertex_normals[map_name]

    # not sure if the following can fail if vertex normal map misses values ?!
    # all custom split normals pointing up.
    normals = []
    for vert in mesh.vertices:
        try:
            normals.append(lxo_vertex_normals[vert.index])
        except (IndexError, KeyError):
            normals.append((0.0, 0.0, 0.0))
    mesh.normals_split_custom_set_from_vertices(normals)

    try:
        vertex_normals_disco = lxo_layer.vertex_normals_disco[map_name]
    except KeyError:
        # return early if there is no disco map
        return

    # fill with vertex normals, maybe "(use zero-vectors to keep auto ones)" ?
    normals = [lxo_vertex_normals[loop.vertex_index] for loop in mesh.loops]

    for poly_index in vertex_normals_disco.keys():
        for vert_index, normal in vertex_normals_disco[poly_index].items():
            for loop_index in mesh.polygons[poly_index].loop_indices:
                if vert_index == mesh.loops[loop_index].vertex_index:
                    print(vert_index, loop_index, normal)
                    normals[loop_index] = normal

    mesh.normals_split_custom_set(normals)


def shade_smooth():
    # Cache the current selection
    current_selection = bpy.context.selected_objects

    # Select no objects
    bpy.ops.object.select_all(action='DESELECT')

    # Select all meshes
    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            obj.select_set(True)

    # Shade smooth
    bpy.ops.object.shade_smooth()

    # Restore the previous selection
    bpy.ops.object.select_all(action='DESELECT')
    for obj in current_selection:
        obj.select_set(True)


def build_objects(lxo: lxo_reader.LXOFile, load_materials: bool, clean_import: bool, global_matrix):
    """Using the gathered data, create the objects."""
    ob_dict = {}  # Used for the parenting setup.
    mesh_dict = {}  # used to match layers to items
    transforms_dict: dict[int, dict[int, lxo_reader.LXOItem]] = {}  # used to match transforms to items
    light_materials = {}  # used to match lightmaterial to light for color
    shadertree_items: dict[str, lxo_reader.LXOItem] = {}  # collect all items for materials

    # Before adding any meshes or armatures go into Object mode.
    # TODO: is this needed?
    if bpy.ops.object.mode_set.poll():
        bpy.ops.object.mode_set(mode="OBJECT")

    if clean_import:
        bpy.ops.wm.read_homefile(use_empty=True)

    # create all items
    for lxo_item in lxo.items:
        item_name = lxo_item.vname if lxo_item.vname else lxo_item.name
        if item_name is None:
            item_name = lxo_item.typename
        object_data = None

        if lxo_item.typename in ['translation', 'rotation', 'scale']:
            item_index, link_index = lxo_item.graph_links['xfrmCore'] if 'xfrmCore' in lxo_item.graph_links else (-1, -1)
            print(item_index, link_index, item_name)
            if item_index == -1:
                # seems to be some issue with texture locators
                continue
            if item_index in transforms_dict:
                transforms_dict[item_index][link_index] = lxo_item
            else:
                transforms_dict[item_index] = {link_index: lxo_item}
        elif lxo_item.typename == "lightMaterial":
            item_index, link_index = lxo_item.graph_links['parent']
            # assuming just one lightmaterial per light right now
            light_materials[item_index] = lxo_item
        elif lxo_item.typename in ["advancedMaterial", "mask", "polyRender"]:
            # TODO: improve this mapping
            shadertree_items[lxo_item.id] = lxo_item
        elif lxo_item.typename == "mesh":
            object_data = bpy.data.meshes.new(item_name)
            mesh_dict[lxo_item.id] = object_data
        elif lxo_item.typename == "camera":
            object_data = bpy.data.cameras.new(item_name)
            # saved as float in meters, we want mm
            object_data.lens = int(lxo_item.channel['focalLen'] * 1000)
            # object_data.dof.aperture_fstop = lxoItem.channel['fStop']
        elif lxo_item.typename[-5:] == "Light":
            object_data = create_light(lxo_item, item_name, light_materials)

        if lxo_item.LAYR is not None:
            # only locator type items should have a LAYR chunk
            # (= anything in item tree)
            # create empty for object data and add to scene
            ob = bpy.data.objects.new(name=item_name, object_data=object_data)
            scn = bpy.context.collection
            scn.objects.link(ob)

            parent_index = None
            if "parent" in lxo_item.graph_links:
                # 0 is itemIndex, 1 is linkIndex
                # TODO: handle linkIndex, not sure if super important
                parent_index = lxo_item.graph_links["parent"][0]
            ob_dict[lxo_item.id] = [ob, parent_index]

    # figure out materials
    materials: dict[str, lxo_reader.LXOItem] = {}
    for lxo_item in shadertree_items.values():
        if lxo_item.typename == "advancedMaterial":
            parent_index = lxo_item.graph_links['parent'][0]
            parent_item = shadertree_items[parent_index]
            if parent_item.typename == 'polyRender':
                continue
            material_name = parent_item.channel['ptag']
            materials[material_name] = lxo_item

    # TODO: OOO transforms from Modo...
    for item_index, transforms in transforms_dict.items():
        blender_object = ob_dict[item_index][0]
        for _, lxo_item in sorted(transforms.items()):
            if lxo_item.typename == "scale":
                try:
                    data = lxo_item.CHNV['scl']
                except KeyError:
                    # TODO: verify this fix
                    data = ((0, 1), (1, 1), (2, 1))
                scl = (data[0][1], data[1][1], data[2][1])
                blender_object.scale = scl
            elif lxo_item.typename == "rotation":
                try:
                    data = lxo_item.CHNV['rot']
                except KeyError:
                    # TODO: verify this fix
                    data = ((0, 0), (1, 0), (2, 0))
                rot = Euler((data[0][1], data[1][1], data[2][1]), 'ZXY')
                blender_object.rotation_euler = rot
                # TODO read euler order from item
                blender_object.rotation_mode = 'ZXY'
            elif lxo_item.typename == "translation":
                try:
                    data = lxo_item.CHNV['pos']
                except KeyError:
                    # TODO: verify this fix
                    data = ((0, 0), (1, 0), (2, 0))
                pos = (data[0][1], data[1][1], data[2][1])
                blender_object.location = pos


    mat_lxo_blender_mapping_vector = {
        "diffCol": "Base Color",
        #"subsCol": "Subsurface Color",
        #"lumiCol": "Emission",
    }

    material_lxo_blender_mapping = {
        "subsAmt": "Subsurface",
        "metallic": "Metallic",
        "specAmt": "Specular",
        "specTint": "Specular Tint",
        "rough": "Roughness",
        "sheen": "Sheen",
        "sheenTint": "Sheen Tint",
        "coatAmt": "Clearcoat",
        "coatRough": "Clearcoat Roughness",
        "tranAmt": "Transmission",
        "tranRough": "Transmission Roughness",
        #"radiance": "Emission",
    }

    # match mesh layers to items
    for lxo_layer in lxo.layers:
        try:
            mesh = mesh_dict[lxo_layer.reference_id]
        except KeyError:
            print(f"error with {lxo_layer.reference_id} {lxo_layer.name}")
            continue
        # adapt to blender coord system and right up axis
        points = [[p[0], p[1], -p[2]] for p in lxo_layer.points]
        # correcting default polygon normals
        for point_list in lxo_layer.polygons:
            point_list.reverse()
        mesh.from_pydata(points, [], lxo_layer.polygons)

        # create uvmaps
        if len(lxo_layer.uv_maps_disco) > 0 or len(lxo_layer.uv_maps) > 0:
            create_uvmaps(lxo_layer, mesh)

        # add materials and tags
        if load_materials:
            lxo_layer.generate_materials()
            mat_slot = 0
            for material_name, polygons in lxo_layer.materials.items():
                new_material = bpy.data.materials.new(material_name)
                # TODO: this is only for principled shader
                new_material.use_nodes = True
                # adding alpha value
                try:
                    lxo_material = materials[material_name]
                except KeyError:
                    # TODO handle material errors
                    continue
                # diffColor = [val[1] for val in lxoMaterial.CHNV['diffCol']] + [1, ]
                # newMaterial.diffuse_color = diffColor
                for lxo_val, bpy_val in mat_lxo_blender_mapping_vector.items():
                    print(lxo_val, bpy_val)
                    color = [val[1] for val in lxo_material.CHNV[lxo_val]] + [1, ]
                    new_material.node_tree.nodes['Principled BSDF'].inputs[bpy_val].default_value = color
                emission = lxo_material.channel["radiance"]
                emission_color = [val[1] * emission for val in lxo_material.CHNV["lumiCol"]] + [1, ]
                new_material.node_tree.nodes['Principled BSDF'].inputs["Emission"].default_value = emission_color
                for lxo_val, bpy_val in material_lxo_blender_mapping.items():
                    print(lxo_val, bpy_val)
                    new_material.node_tree.nodes['Principled BSDF'].inputs[bpy_val].default_value = lxo_material.channel[lxo_val]

                mesh.materials.append(new_material)
                for index in polygons:
                    mesh.polygons[index].material_index = mat_slot
                    mesh.polygons[index].use_smooth = True
                # ok-ish for now
                #mesh.use_auto_smooth = True
                # not perfect, in Modo smoothing is part of the material
                # in blender it's part of the mesh
                #mesh.auto_smooth_angle = lxo_material.channel['smAngle']

                mat_slot += 1

        # vertex normal maps
        if (len(lxo_layer.vertex_normals) > 0 or
                len(lxo_layer.vertex_normals_disco) > 0):
            create_normals(lxo_layer, mesh)

        # add subd modifier is _any_ subD in mesh
        # TODO: figure out how to deal with partial SubD and PSubs
        if lxo_layer.is_subd:
            ob = ob_dict[lxo_layer.reference_id][0]
            ob.modifiers.new(name="Subsurf", type="SUBSURF")
            # TODO: clean up the smoothing mess
            for poly in ob.data.polygons:
                poly.use_smooth = True

    # update view layer for recalc of world matrices
    bpy.context.view_layer.update()

    # parent objects and transform to world orientation
    for ob_key in ob_dict:
        if ob_dict[ob_key][1] is not None and ob_dict[ob_key][1] in ob_dict:
            parent_ob = ob_dict[ob_dict[ob_key][1]]
            ob_dict[ob_key][0].parent = parent_ob[0]
            # ob_dict[ob_key][0].location -= parent_ob[0].location
            print("parenting %s to %s" % (ob_dict[ob_key][0], parent_ob))
        elif ob_dict[ob_key][1] is None:
            # transform root level items with global_matrix
            obj = ob_dict[ob_key][0]
            obj.matrix_world = global_matrix @ obj.matrix_world


def load(operator, context, filepath="",
         axis_forward='-Z',
         axis_up='Y',
         global_scale=1.0,
         ADD_SUBD_MOD=False,
         LOAD_MATERIALS=False,
         LOAD_HIDDEN=False,
         CLEAN_IMPORT=False):

    from bpy_extras.io_utils import axis_conversion
    global_matrix = (Matrix.Scale(global_scale, 4) @
                     axis_conversion(from_forward=axis_forward,
                                     from_up=axis_up).to_4x4())

    importlib.reload(lxo_reader)
    lxo_read = lxo_reader.LXOReader()
    lxo = lxo_read.read_from_file(filepath)

    # lwo.resolve_clips()
    # lwo.validate_lwo()
    build_objects(lxo, LOAD_MATERIALS, CLEAN_IMPORT, global_matrix)

    del lxo
    # With the data gathered, build the object(s).
    return {"FINISHED"}
