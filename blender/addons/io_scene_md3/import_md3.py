# TODO: different normals for shape keys
# TODO: merge vertices near sharp edges (there is a disconnected surface now)
# TODO: use_smooth=False for flat faces (all vertex normal equal)


# from typing import Collection
#from msvcrt import kbhit
import bpy
import os.path

from . import fmt_md3 as fmt
from mathutils import Vector, Matrix  # hy:
from .utils import (  # hy: backward compatable
    set_select_state,
    get_uv_data,
    get_objects,
    set_empty_draw_type,
)


def guess_texture_filepath(modelpath, imagepath):
    fileexts = ('', '.png', '.tga', '.jpg', '.jpeg')
    modelpath = os.path.normpath(os.path.normcase(modelpath))
    modeldir, _ = os.path.split(modelpath)
    imagedir, imagename = os.path.split(os.path.normpath(os.path.normcase(imagepath)))
    previp = None
    ip = imagedir
    while ip != previp:
        if ip in modeldir:
            pos = modeldir.rfind(ip)
            nameguess = os.path.join(modeldir[:pos + len(ip)], imagedir[len(ip):], imagename)
            for ext in fileexts:
                yield nameguess + ext
        previp = ip
        ip, _ = os.path.split(ip)
    nameguess = os.path.join(modeldir, imagename)
    for ext in fileexts:
        yield nameguess + ext


def get_tag_matrix_basis(data):
    basis = Matrix.Identity(4)
    for j in range(3):
        basis[j].xyz = data.axis[j::3]
    basis.translation = Vector(data.origin)
    return basis


class MD3_Combine_KP:
    def __init__(self, context):
        self.context = context

    def __call__(self):
        array_legs = []
        array_body = []
        array_head = []
        array_wep = []
        # tag_legs_nodeID = None
        self.tag_body_nodeID = None
        self.tag_head_nodeID = None
        self.tag_wep_nodeID = None
        self.tag_flash_nodeID = None

        def setupObjectsAsGroups_fn(self):

            def move_tagToTop(self, array_, tag_name):
                sLen = len(tag_name)
                for x in range(0, len(array_)):
                    tmpStr = array_[x].name[:sLen]
                    if tmpStr == tag_name:
                        array_[0], array_[x] = array_[x], array_[0]  # swap
                        break  # exit  # found
                return array_
            # end move_tagToTop

            for obj in self.objects:
                if not (obj.type == 'MESH') and not (obj.type == 'EMPTY'):
                    continue

                firstletter = obj.name[0:2]  # substring obj.name 1 2 as name
                tagname = obj.name[0:4]  # substring obj.name 1 4 as name
                objectsName = obj.name  # string

                # asigne each part to a group. eg.. tag_torso to group_body
                discard = True
                if (tagname == "tag_"):
                    if objectsName[:9] == "tag_torso":
                        if objectsName[9:13] == ".low":
                            self.tag_body_nodeID = obj
                            array_legs.append(obj)
                            discard = False
                    elif objectsName[:8] == "tag_head":
                        if objectsName[8:12] == ".upp":
                            self.tag_head_nodeID = obj
                            array_head.append(obj)
                            discard = False
                    elif objectsName[:10] == "tag_weapon":
                        if objectsName[10:14] == ".upp":
                            self.tag_wep_nodeID = obj
                            array_body.append(obj)
                            discard = False
                    elif objectsName[:9] == "tag_flash":
                        # if objectsName[9:13] == ".sho":  # note only 1
                        self.tag_flash_nodeID = obj
                        array_wep.append(obj)
                        discard = False
                    if discard:
                        print("%-14s %s" % ("Discard tag:", objectsName))
                        continue
                #  end tag asigments
                elif (firstletter == "l_"):
                    array_legs.append(obj)
                elif (firstletter == "u_"):
                    array_body.append(obj)
                elif (firstletter == "w_"):
                    array_wep.append(obj)
                elif (firstletter == "h_"):
                    array_head.append(obj)
                else:
                    print("%-14s %s" % ("Discard object:", obj.name))
                    continue

                print("%-14s %s" % ("added object:", obj.name))
            #  end adding each mesh object to array

            # sort list
            move_tagToTop(self, array_legs, "tag_torso")
            move_tagToTop(self, array_body, "tag_weapon")
            move_tagToTop(self, array_head, "tag_head")
            move_tagToTop(self, array_wep, "tag_flash")

            print("---- Finished Grouping items -----")
        # end function set model groups

        def moveChild_tag_fn(child_f, parent_f):
            if parent_f is None or child_f is None:
                return

            child_f.parent = parent_f

        def moveChild_mesh_fn(grouped_md3_f, parent_f):
            if parent_f is None:
                return
            for child in grouped_md3_f:
                if (child.name[:4] == "tag_" or child.parent):
                    continue
                child.parent = parent_f
                child.location = (0, 0, 0)
                child.rotation_quaternion = (1, 0, 0, 0)
        # end moveChild_mesh_fn

        self.objects = bpy.context.visible_objects
        setupObjectsAsGroups_fn(self)
        moveChild_mesh_fn(array_wep, self.tag_wep_nodeID)  # self.obj_out
        moveChild_mesh_fn(array_head, self.tag_head_nodeID)
        moveChild_mesh_fn(array_body, self.tag_body_nodeID)

        # move tag to tag/parent then link
        moveChild_tag_fn(self.tag_flash_nodeID, self.tag_wep_nodeID)  # move tag_flash to tag_wep
        moveChild_tag_fn(self.tag_wep_nodeID, self.tag_body_nodeID)  # move tag_wep to tag_body
        moveChild_tag_fn(self.tag_head_nodeID, self.tag_body_nodeID)  # move tag_head to tag_body


class MD3Importer_KP:
    def __init__(self, context):
        self.context = context

    @property
    def scene(self):
        return self.context.scene

    def read_n_items(self, n, offset, func):
        self.file.seek(offset)
        return [func(i) for i in range(n)]

    def unpack(self, rtype):
        return rtype.funpack(self.file)

    def read_frame(self, i):
        return self.unpack(fmt.Frame)

    def create_tag(self, i):
        data = self.unpack(fmt.Tag)
        bpy.ops.object.add(type='EMPTY')
        tag = bpy.context.object
        tag.name = data.name
        tag.name += '.' + self.fNameMD3  # hy: append group name it belongs to
        set_empty_draw_type(tag, 'ARROWS')  # tag.empty_draw_type = 'ARROWS'
        tag.rotation_mode = 'QUATERNION'
        tag.matrix_basis = get_tag_matrix_basis(data)
        set_select_state(context=tag, opt=False)  # hy: de-select
        return tag

    def read_tag_frame(self, i):
        tag = self.tags[i % self.header.nTags]
        data = self.unpack(fmt.Tag)
        tag.matrix_basis = get_tag_matrix_basis(data)
        frame = i // self.header.nTags
        tag.keyframe_insert('location', frame=frame, group='LocRot')
        tag.keyframe_insert('rotation_quaternion', frame=frame, group='LocRot')

    def read_surface_triangle(self, i):
        data = self.unpack(fmt.Triangle)
        ls = i * 3
        self.mesh.loops[ls].vertex_index = data.a
        self.mesh.loops[ls + 1].vertex_index = data.c  # swapped
        self.mesh.loops[ls + 2].vertex_index = data.b  # swapped
        self.mesh.polygons[i].loop_start = ls
        #self.mesh.polygons[i].loop_total = 3
        self.mesh.polygons[i].use_smooth = True

    def read_surface_vert(self, i):
        data = self.unpack(fmt.Vertex)
        self.verts[i].co = Vector((data.x, data.y, data.z))
        # ignoring data.normal here

    def read_surface_normals(self, i):
        data = self.unpack(fmt.Vertex)
        self.mesh.vertices[i].normal = Vector(data.normal)

    def read_mesh_animation(self, obj, data, start_pos):
        obj.shape_key_add(name=self.frames[0].name)  # adding first frame, which is already loaded
        self.mesh.shape_keys.use_relative = False
        # TODO: ensure MD3 has linear frame interpolation
        for frame in range(1, data.nFrames):  # first frame skipped
            shape_key = obj.shape_key_add(name=self.frames[frame].name)
            self.verts = shape_key.data
            self.read_n_items(
                data.nVerts,
                start_pos + data.offVerts + frame * fmt.Vertex.size * data.nVerts,
                self.read_surface_vert)
        get_objects(bpy.context).active = obj  # bpy.context.view_layer.objects.active = obj
        self.context.object.active_shape_key_index = 0
        # bpy.ops.object.shape_key_retime()  # hy: causes key 0 to shift to 10.0 in 2.79
        # ofs = 1 if bpy.app.version < (2, 80) else 0
        for frame in range(data.nFrames):
            self.mesh.shape_keys.eval_time = 10.0 * (frame)  # + ofs) hy: starts at 0
            self.mesh.shape_keys.keyframe_insert('eval_time', frame=frame)

        # hy: fix for kp using non integer frame placement. this will help Q3 editing too
        for sk in self.mesh.shape_keys.key_blocks:
            sk.interpolation = 'KEY_LINEAR'  # 'KEY_CARDINAL', 'KEY_CATMULL_ROM', 'KEY_BSPLINE')

    def read_surface_ST(self, i):
        data = self.unpack(fmt.TexCoord)
        return (data.s, data.t)

    def make_surface_UV_map(self, uv, uvdata):
        for poly in self.mesh.polygons:
            for i in range(poly.loop_start, poly.loop_start + poly.loop_total):
                vidx = self.mesh.loops[i].vertex_index
                uvdata[i].uv = uv[vidx]
            # uvdata[i].image

    def read_surface_shader(self, i):
        data = self.unpack(fmt.Shader)
        # hy:
        # get materal node/links
        self.material.use_nodes = True
        mat_nodes = self.material.node_tree.nodes
        mat_links = self.material.node_tree.links
        # delete existing nodes
        while(mat_nodes):
            mat_nodes.remove(mat_nodes[0])

        # create diffuse/texture/output nodes
        node_tex = mat_nodes.new("ShaderNodeTexImage")  # image texture
        node_diff = mat_nodes.new(type='ShaderNodeBsdfDiffuse')  # simple shader
        node_out_mat = mat_nodes.new(type='ShaderNodeOutputMaterial')  # output Cycles
        # move nodes
        node_tex.location = Vector((-350, -80))
        node_out_mat.location = Vector((250, 0))
        # create links
        mat_links.new(node_diff.outputs['BSDF'], node_out_mat.inputs['Surface'])
        mat_links.new(node_tex.outputs['Color'], node_diff.inputs['Color'])

        if bpy.app.version < (2, 80):  # output blender render v2.79
            node_output = mat_nodes.new(type='ShaderNodeOutput')
            mat_links.new(node_tex.outputs['Color'], node_output.inputs['Color'])
            node_output.location = Vector((250, -120))

        for fname in guess_texture_filepath(self.filename, data.name):
            if '\0' in fname:  # preventing ValueError: embedded null byte
                continue
            if os.path.isfile(fname):
                image = bpy.data.images.load(fname)  # TODO check duplicates?
                node_tex.image = image
                break

        # missing
        if node_tex.image is None:
            print("missing texture")
            image = bpy.data.images.new(data.name, 256, 256)
            node_tex.image = image

    def read_surface(self, i):
        start_pos = self.file.tell()

        data = self.unpack(fmt.Surface)
        assert data.magic == b'IDP3'
        assert data.nFrames == self.header.nFrames
        assert data.nShaders <= 256
        if data.nVerts > 4096:
            print('Warning: md3 surface contains too many vertices')
        if data.nTris > 8192:
            print('Warning: md3 surface contains too many triangles')

        self.mesh = bpy.data.meshes.new(data.name)
        self.mesh.vertices.add(count=data.nVerts)
        self.mesh.polygons.add(count=data.nTris)
        self.mesh.loops.add(count=data.nTris * 3)

        self.read_n_items(data.nTris, start_pos + data.offTris, self.read_surface_triangle)
        self.verts = self.mesh.vertices
        self.read_n_items(data.nVerts, start_pos + data.offVerts, self.read_surface_vert)

        self.mesh.validate()
        #self.mesh.calc_normals()

        self.material = bpy.data.materials.new('Main')  # hy: TODO shader/.skin
        self.mesh.materials.append(self.material)

        get_uv_data(self.mesh).new(name='UVMap')
        self.make_surface_UV_map(
            self.read_n_items(data.nVerts, start_pos + data.offST, self.read_surface_ST),
            self.mesh.uv_layers['UVMap'].data)

        self.read_n_items(data.nShaders, start_pos + data.offShaders, self.read_surface_shader)

        obj = bpy.data.objects.new(data.name, self.mesh)
        self.mesh_collect.objects.link(obj)

        if data.nFrames > 1:
            self.read_mesh_animation(obj, data, start_pos)

        self.file.seek(start_pos + data.offEnd)

    def __call__(self, filename, ui_attach):
        self.filename = filename
        self.ui_attach = ui_attach

        with open(filename, 'rb') as file:
            self.file = file

            self.header = self.unpack(fmt.Header)
            assert self.header.magic == fmt.MAGIC
            assert self.header.version == fmt.VERSION

            name = os.path.split(filename)[1].replace('.md3', '')
            self.fNameMD3 = name
            if bpy.app.version < (2, 80):
                # group model into 1 scene.
                if not self.scene.name == 'Quake3_models':
                    bpy.ops.scene.new()
                    self.scene.name = 'Quake3_models'  # self.header.modelname
                # self.mesh_collect = bpy.context.scene.layers
                self.mesh_collect = self.scene
            else:
                # make a mesh group
                self.mesh_collect = bpy.data.collections.new(name)
                bpy.context.scene.collection.children.link(self.mesh_collect)
                col = bpy.context.view_layer.layer_collection.children[self.mesh_collect.name]
                bpy.context.view_layer.active_layer_collection = col

            self.scene.frame_start = 0
            if (self.scene.frame_end < self.header.nFrames):  # hy: only set if above frame_end
                self.scene.frame_end = self.header.nFrames - 1

            self.frames = self.read_n_items(self.header.nFrames, self.header.offFrames, self.read_frame)
            self.tags = self.read_n_items(self.header.nTags, self.header.offTags, self.create_tag)
            if self.header.nFrames > 1:
                self.read_n_items(self.header.nTags * self.header.nFrames, self.header.offTags, self.read_tag_frame)
            self.read_n_items(self.header.nSurfaces, self.header.offSurfaces, self.read_surface)

        self.scene.frame_set(0)
