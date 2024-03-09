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
import bmesh
import mathutils
from .gen_material import lwo2BI, lwo2cycles, get_existing


def create_mappack(data, map_name, map_type):
    """Match the map data to faces."""
    pack = {}

    def color_pointmap(map):
        for fi in range(len(data.pols)):
            if fi not in pack:
                pack[fi] = []
            for pnt in data.pols[fi]:
                if pnt in map:
                    pack[fi].append(map[pnt])
                else:
                    pack[fi].append((1.0, 1.0, 1.0))

    def color_facemap(map):
        for fi in range(len(data.pols)):
            if fi not in pack:
                pack[fi] = []
                for p in data.pols[fi]:
                    pack[fi].append((1.0, 1.0, 1.0))
            if fi in map:
                for po in range(len(data.pols[fi])):
                    if data.pols[fi][po] in map[fi]:
                        pack[fi].insert(po, map[fi][data.pols[fi][po]])
                        del pack[fi][po + 1]

    if map_type == "COLOR":
        # Look at the first map, is it a point or face map
        if "PointMap" in data.colmaps[map_name]:
            color_pointmap(data.colmaps[map_name]["PointMap"])

        if "FaceMap" in data.colmaps[map_name]:
            color_facemap(data.colmaps[map_name]["FaceMap"])

    return pack


def build_armature(layer_data, bones):
    """Build an armature from the skelegon data in the mesh."""
    print("Building Armature")

    # New Armatures include a default bone, remove it.
    bones.remove(bones[0])

    # Now start adding the bones at the point locations.
    prev_bone = None
    for skb_idx in range(len(layer_data.bones)):
        if skb_idx in layer_data.bone_names:
            nb = bones.new(layer_data.bone_names[skb_idx])
        else:
            nb = bones.new("Bone")

        nb.head = layer_data.pnts[layer_data.bones[skb_idx][0]]
        nb.tail = layer_data.pnts[layer_data.bones[skb_idx][1]]

        if skb_idx in layer_data.bone_rolls:
            xyz = layer_data.bone_rolls[skb_idx].split(" ")
            vec = mathutils.Vector((float(xyz[0]), float(xyz[1]), float(xyz[2])))
            quat = vec.to_track_quat("Y", "Z")
            nb.roll = max(quat.to_euler("YZX"))
            if nb.roll == 0.0:
                nb.roll = min(quat.to_euler("YZX")) * -1
            # YZX order seems to produce the correct roll value.
        else:
            nb.roll = 0.0

        if prev_bone is not None:
            if nb.head == prev_bone.tail:
                nb.parent = prev_bone

        nb.use_connect = True
        prev_bone = nb


def build_materials(lwo, ch):
    print(f"Adding {len(lwo.surfs)} Materials")

    renderer = bpy.context.scene.render.engine
    for key, surf in lwo.surfs.items():
        m = get_existing(surf, ch.use_existing_materials)
        if None == m:
            if (
                "CYCLES" == renderer
                or "BLENDER_EEVEE" == renderer
                or "BLENDER_WORKBENCH" == renderer
            ):
                m = lwo2cycles(surf)
            else:
                m = lwo2BI(surf)
        lwo.materials[key] = m


def build_objects(lwo, ch):
    """Using the gathered data, create the objects."""
    ob_dict = {}  # Used for the parenting setup.

    build_materials(lwo, ch)

    # Single layer objects use the object file's name instead.
    if len(lwo.layers) and lwo.layers[-1].name == "Layer 1":
        lwo.layers[-1].name = lwo.name
        print(f"Building '{lwo.name}' Object")
    else:
        print(f"Building {len(lwo.layers)} Objects")

    # Before adding any meshes or armatures go into Object mode.
    if bpy.ops.object.mode_set.poll():
        bpy.ops.object.mode_set(mode="OBJECT")

    for layer_data in lwo.layers:
        face_edges = []
        me = bpy.data.meshes.new(layer_data.name)
        me.from_pydata(layer_data.pnts, face_edges, layer_data.pols)
        #me.validate()
        
        # https://developer.blender.org/T75884 
        check_ngons = True
#         for i, pol in enumerate(layer_data.pols):
#             if 1 == len(layer_data.pols[i]):
#                 raise Exception(i, layer_data.pols[i])
#                 check_ngons = False
        
        ob = bpy.data.objects.new(layer_data.name, me)

        scn = bpy.context.collection
        scn.objects.link(ob)
        bpy.context.view_layer.objects.active = ob
        ob.select_set(state=True)







        ob_dict[layer_data.index] = [ob, layer_data.parent_index]

        # Move the object so the pivot is in the right place.
        ob.location = layer_data.pivot

        # Create the Material Slots and assign the MatIndex to the correct faces.
        mat_slot = 0
        for surf_key in layer_data.surf_tags:
            if lwo.tags[surf_key] in lwo.materials:
                me.materials.append(lwo.materials[lwo.tags[surf_key]].mat)

                for fi in layer_data.surf_tags[surf_key]:
                    me.polygons[fi].material_index = mat_slot
                    me.polygons[fi].use_smooth = lwo.materials[
                        lwo.tags[surf_key]
                    ].smooth

                mat_slot += 1

        # Create the Vertex Normals.
        if len(layer_data.vnorms) > 0:
            print("Adding Vertex Normals")
            for vi in layer_data.vnorms.keys():
                me.vertices[vi].normal = layer_data.vnorms[vi]

#         # Create the Split Vertex Normals.
#         print(len(layer_data.lnorms))
#         print(len(layer_data.vnorms))
        #"tests/lwo_nasa/src/Wide Field Infrared Survey Telescope (WFIRST)/WFirst-2015-composite.lwo"
        if len(layer_data.lnorms) > 0 and len(layer_data.vnorms) > 0:
            pass
            #raise Exception
            
#         if len(layer_data.lnorms) > 0:
#             print("Adding Smoothing from Split Vertex Normals")
#             for pi in layer_data.lnorms.keys():
#                 p = me.polygons[pi]
#                 p.use_smooth = False
#                 keepflat = True
#                 for no in layer_data.lnorms[pi]:
#                     vn = layer_data.vnorms[no[0]]
#                     if (
#                            round(no[1], 4) == round(vn[0], 4)
#                         or round(no[2], 4) == round(vn[1], 4)
#                         or round(no[3], 4) == round(vn[2], 4)
#                     ):
#                         keepflat = False
#                         break
#                 if not (keepflat):
#                     p.use_smooth = True
#                 # for li in me.polygons[vn[1]].loop_indices:
#                 #    l = me.loops[li]
#                 #    if l.vertex_index == vn[0]:
#                 #        l.normal = [vn[2], vn[3], vn[4]]

        # Create the Vertex Groups (LW's Weight Maps).
        if len(layer_data.wmaps) > 0:
            print(f"Adding {len(layer_data.wmaps)} Vertex Groups")
            for wmap_key in layer_data.wmaps:
                vgroup = ob.vertex_groups.new()
                vgroup.name = wmap_key
                wlist = layer_data.wmaps[wmap_key]
                for pvp in wlist:
                    vgroup.add((pvp[0],), pvp[1], "REPLACE")

        # Create the Shape Keys (LW's Endomorphs).
        if len(layer_data.morphs) > 0:
            print(f"Adding {len(layer_data.morphs)} Shapes Keys")
            ob.shape_key_add(name="Basis")  # Got to have a Base Shape.
            for morph_key in layer_data.morphs:
                skey = ob.shape_key_add(name=morph_key)
                dlist = layer_data.morphs[morph_key]
                for pdp in dlist:
                    me.shape_keys.key_blocks[skey.name].data[pdp[0]].co = [
                        pdp[1],
                        pdp[2],
                        pdp[3],
                    ]

        # Create the Vertex Color maps.
        if len(layer_data.colmaps) > 0:
            print(f"Adding {len(layer_data.colmaps)} Vertex Color Maps")
            for cmap_key in layer_data.colmaps:
                map_pack = create_mappack(layer_data, cmap_key, "COLOR")
                vertexColorMap = me.vertex_colors.new(name=cmap_key)

                for poly in me.polygons:                   
                    if poly.index in map_pack:
                        colors = map_pack[poly.index]
                        for i, loop_index in enumerate(poly.loop_indices):
                            vertexColorMap.data[loop_index].color = colors[i] + (1.0,)
                            
        # Create the UV Maps.
        if len(layer_data.uvmaps_vmad) > 0 or len(layer_data.uvmaps_vmap) > 0:
            allmaps = set(list(layer_data.uvmaps_vmad.keys()))
            allmaps = sorted(allmaps.union(set(list(layer_data.uvmaps_vmap.keys()))))
            print(f"Adding {len(allmaps)} UV Textures")
            if len(allmaps) > 8:
                print(f"This mesh contains more than 8 UVMaps: {len(allmaps)}")
            
            for uvmap_key in allmaps:

                uvm = me.uv_layers.new()



                if None == uvm:
                    break
                uvm.name = uvmap_key

            vertloops = {}
            for v in me.vertices:
                vertloops[v.index] = []
            for l in me.loops:
                vertloops[l.vertex_index].append(l.index)
            for uvmap_key in layer_data.uvmaps_vmad.keys():
                uvcoords = layer_data.uvmaps_vmad[uvmap_key]["FaceMap"]
                uvm = me.uv_layers.get(uvmap_key)
                if None == uvm:
                    continue
                for pol_id in uvcoords.keys():
                    for pnt_id, (u, v) in uvcoords[pol_id].items():
                        for li in me.polygons[pol_id].loop_indices:
                            if pnt_id == me.loops[li].vertex_index:
                                uvm.data[li].uv = [u, v]
                                break
            for uvmap_key in layer_data.uvmaps_vmap.keys():
                uvcoords = layer_data.uvmaps_vmap[uvmap_key]["PointMap"]
                uvm = me.uv_layers.get(uvmap_key)
                if None == uvm:
                    continue
                for pnt_id, (u, v) in uvcoords.items():
                    for li in vertloops[pnt_id]:
                        uvm.data[li].uv = [u, v]


        # Apply the Edge Weighting.
        if len(layer_data.edge_weights) > 0:
            for edge in me.edges:
                edge_sa = "{0} {1}".format(edge.vertices[0], edge.vertices[1])
                edge_sb = "{0} {1}".format(edge.vertices[1], edge.vertices[0])
                if edge_sa in layer_data.edge_weights:
                    edge.crease = layer_data.edge_weights[edge_sa]
                elif edge_sb in layer_data.edge_weights:
                    edge.crease = layer_data.edge_weights[edge_sb]

        # Now triangulate the NGons.
        # if not 0 == len(ngons):
        #if True:
        if check_ngons:
            bm = bmesh.new()
            bm.from_mesh(me) # Causes crashed in star field
            if hasattr(bm.faces, "ensure_lookup_table"):
                bm.faces.ensure_lookup_table()

            faces = []
            for face in bm.faces:
                if len(face.verts) > 4:  # review this number
                    faces.append(face)
            print(f"{len(faces)} NGONs")
            bmesh.ops.triangulate(bm, faces=faces)

            # Finish up, write the bmesh back to the mesh
            bm.to_mesh(me)
            bm.free()

        # We may have some invalid mesh data, See: [#27916]
        # keep this last!
        print(f"Validating mesh: {me.name}...")
        me.validate()

        # Unfortunately we can't exlude certain faces from the subdivision.
        if layer_data.has_subds and ch.add_subd_mod:
            ob.modifiers.new(name="Subsurf", type="SUBSURF")
        
        ob.modifiers.new(name= "Edge Split", type="EDGE_SPLIT")

        # Should we build an armature from the embedded rig?
        if len(layer_data.bones) > 0 and ch.skel_to_arm:
            bpy.ops.object.armature_add()
            arm_object = bpy.context.active_object
            arm_object.name = "ARM_" + layer_data.name
            arm_object.data.name = arm_object.name
            arm_object.location = layer_data.pivot
            bpy.ops.object.mode_set(mode="EDIT")
            build_armature(layer_data, arm_object.data.edit_bones)
            bpy.ops.object.mode_set(mode="OBJECT")

        # Clear out the dictionaries for this layer.
        layer_data.bone_names.clear()
        layer_data.bone_rolls.clear()
        layer_data.wmaps.clear()
        layer_data.colmaps.clear()
        layer_data.uvmaps_vmad.clear()
        layer_data.uvmaps_vmap.clear()
        layer_data.morphs.clear()
        layer_data.surf_tags.clear()


        # Texture slots have been removed from 2.80, is there a corresponding any thing?
        # Create the 3D View visualisation textures.
        if (
            "CYCLES" == bpy.context.scene.render.engine
            or "BLENDER_EEVEE" == bpy.context.scene.render.engine
        ):
            pass
        else:
            for tf in me.polygons:
                tex_slots = me.materials[tf.material_index].texture_slots
                for ts in tex_slots:
                    if ts:
                        if None == tex_slots[0].texture:
                            continue

                        image = tex_slots[0].texture.image
                        for lay in me.tessface_uv_textures:
                            lay.data[tf.index].image = image
                        break

        print("done!")

    # With the objects made, setup the parents and re-adjust the locations.
    if len(ob_dict.keys()) > 1:
        empty = bpy.data.objects.new(name=lwo.name + "_empty", object_data=None)

        bpy.context.collection.objects.link(empty)



    for ob_key in ob_dict:
        if ob_dict[ob_key][1] != -1 and ob_dict[ob_key][1] in ob_dict:
            parent_ob = ob_dict[ob_dict[ob_key][1]]
            ob_dict[ob_key][0].parent = parent_ob[0]
            ob_dict[ob_key][0].location -= parent_ob[0].location
        elif len(ob_dict.keys()) > 1:
            ob_dict[ob_key][0].parent = empty


    bpy.context.view_layer.update()




    print("Done Importing LWO File")
