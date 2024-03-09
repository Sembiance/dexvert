from __future__ import annotations
import sys
import struct
import array
from bpy_extras.image_utils import load_image
import bpy
import os
from .xfile_parser import XFileParser


def convert_mesh(mesh, basepath: str):
    from bpy_extras import node_shader_utils

    # vertex list
    positions = []
    normals = []
    uvs = []
    materialIndices = []
    triangleCount = 0
    for i in range(len(mesh.posFaces)):
        if len(mesh.posFaces[i].indices) == 3:
            # triangle
            indexLine = [0, 1, 2]
            materialIndices.append(mesh.faceMaterials[i])
            triangleCount += 1
        elif len(mesh.posFaces[i].indices) == 4:
            # Quadrilateral
            indexLine = [0, 1, 2, 0, 2, 3]
            materialIndices.append(mesh.faceMaterials[i])
            materialIndices.append(mesh.faceMaterials[i])
            triangleCount += 2
        else:
            raise ValueError()
        for j in indexLine:
            positions.append(mesh.positions[mesh.posFaces[i].indices[j]])
            normals.append(mesh.normals[mesh.normalFaces[i].indices[j]])
            if mesh.numTextures > 0:
                a = mesh.texCoords[mesh.posFaces[i].indices[j]]
                uvs.append(a)
    # index list
    """
    indicesPerMaterial = []
    for i in range(len(mesh.materials)):
        indicesPerMaterial.append([])
    for i in range(len(materialIndices)):
        indicesPerMaterial[materialIndices[i]].append(i);
    indexCounts = [0] * len(indicesPerMaterial)
    indexBufferSource = []
    indexBufferSourceIndex = 0;
    for i in range(len(indicesPerMaterial)):
        for j in range(len(indicesPerMaterial[i])):
            offset = indicesPerMaterial[i][j] * 3
            indexBufferSource.append((offset + 0, offset + 1, offset + 2))
            indexBufferSourceIndex+=1
        indexCounts[i] = len(indicesPerMaterial[i])
    """
    indexBufferSource = []
    for i in range(len(materialIndices)):
        indexBufferSource.append((i*3+0, i*3+1, i*3+2))

    # generate blender mesh
    newMesh = bpy.data.meshes.new('MyMesh')
    newMesh.from_pydata(positions, [], indexBufferSource)
    newMesh.normals_split_custom_set_from_vertices(normals)
    if uvs:
        uvl = newMesh.uv_layers.new(do_init=False)
        uv_data = uvl.data
        for i in range(len(uv_data)):
            uv_data[i].uv = uvs[i]
            uv_data[i].uv[1] = -uv_data[i].uv[1]

    # load textures
    texture_dic = {}
    for oldMat in mesh.materials:
        if oldMat.textures:
            texEntry = oldMat.textures[0]
            if not texEntry.name:
                continue
            # for MMD
            tex_name = texEntry.name.decode('shift-jis')
            tex_name = tex_name.split('*')[0]

            tex_path = os.path.join(basepath, tex_name)
            not_found = False
            try:
                img = bpy.data.images.load(filepath=tex_path)
            except:
                not_found = True
            texture_dic[tex_name] = bpy.data.textures.new(
                os.path.basename(tex_path), type='IMAGE')
            if not not_found:
                texture_dic[tex_name].image = img
                texture_dic[tex_name].image.alpha_mode = 'PREMUL'
            # use alpha
            #texture_dic[tex_name].image.use_alpha = True

    # add material
    for oldMat in mesh.materials:
        temp_material = bpy.data.materials.new(oldMat.name)
        temp_material_wrap = node_shader_utils.PrincipledBSDFWrapper(
            temp_material, is_readonly=False)
        temp_material_wrap.use_nodes = True
        temp_material_wrap.base_color = oldMat.diffuse[:3]
        # temp_material_wrap.specular = oldMat.specularExponent#oldMat.specular
        #temp_material_wrap.specular_tint = oldMat.specularExponent
        #temp_material_wrap.emission_color = oldMat.emissive
        #temp_material_wrap.alpha = oldMat.diffuse[3]
        newMesh.materials.append(temp_material)

        # texture
        if oldMat.textures:
            texEntry = oldMat.textures[0]
            # if temp_material.texture_slots[0] == None:
            #    temp_material.texture_slots.add()
            # for MMD
            tex_name = texEntry.name.decode('shift-jis')
            tex_name = tex_name.split('*')[0]
            temp_material_wrap.base_color_texture.image = texture_dic[tex_name].image
            temp_material_wrap.base_color_texture.texcoords = "UV"
            #temp_material_wrap.base_color_texture.uv_layer = "UV_Data"
            # MMD Settings
            #temp_material_wrap.base_color_texture.use_map_color_diffuse = True
            temp_material_wrap.base_color_texture.use_alpha = True
            #temp_material_wrap.base_color_texture.blend_type = 'MULTIPLY'

    # set material
    for i in range(len(materialIndices)):
        newMesh.polygons[i].material_index = materialIndices[i]

    newMesh.update()

    return newMesh


def convert_node(node, basepath):
    if not node:
        return
    for mesh in node.meshes:
        mesh = convert_mesh(mesh, basepath)
        obj_mesh = bpy.data.objects.new('MyObj', mesh)
        bpy.context.scene.collection.objects.link(obj_mesh)
    for child in node.children:
        convert_node(child, basepath)


def load(filename: str):

    if bpy.ops.object.mode_set.poll():
        bpy.ops.object.mode_set(mode='OBJECT')

    if bpy.ops.object.select_all.poll():
        bpy.ops.object.select_all(action='DESELECT')

    filepath = filename
    basepath = os.path.dirname(filepath)
    with open(filepath, 'br') as f:
        buffer = f.read()
    parser = XFileParser(buffer)
    oldScene = parser.getImportedData()

    for mesh in oldScene.globalMeshes:
        mesh = convert_mesh(mesh, basepath)
        obj_mesh = bpy.data.objects.new('MyObj', mesh)
        bpy.context.scene.collection.objects.link(obj_mesh)
    convert_node(oldScene.rootNode, basepath)

    return
