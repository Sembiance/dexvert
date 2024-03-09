import bpy
try:
	from . import MD2
except ImportError:
	import util.MD2
try:
	from .prepare_skin_paths import * #test
except ModuleNotFoundError:
	from util.prepare_skin_paths import *
import os  # for checking if skin pathes exist


# from https://blender.stackexchange.com/a/110112
def ShowMessageBox(message = "", title = "Message Box", icon = 'INFO'):

	def draw(self, context):
		self.layout.label(text=message)

	bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)


def blender_load_md2(md2_path, displayed_name, use_custom_md2_skin, custom_md2_skin_path):
	"""
	This function uses the information from a md2 dataclass into a blender object.
	This will consist of an animated mesh and its material (which is not much more than the texture.
	For better understanding, steps are:
		- Create the MD2 object containing all information that's inside the loaded md2
		- Get the absolute path of the UV map / skin to load
		- Get necessary information about the mesh (vertices, tris, uv coordinates)
		- Create the scene structure and create the mesh for the first frame
		- Assign UV coordinates to each triangle
		- Create shape animation (Add keyframe to each vertex)
		- Assign skin to mesh
	"""
	""" Create MD2 dataclass object """
	print("md2_path, displayed_name, use_custom_md2_skin, custom_md2_skin_path")
	print(md2_path, displayed_name, use_custom_md2_skin, custom_md2_skin_path)
	print(locals())
	# ImageFile.LOAD_TRUNCATED_IMAGES = True # Necessary for loading jpgs with PIL

	object_path = md2_path  # Kept for testing purposes
	# A dataclass containing all information stored in a .md2 file
	my_object = MD2.load_file(object_path)

	""" Create skin path. By default, the one stored inside of the MD2 is used. Some engines like the Digital Paintball 2 one
	check for any image file with that path disregarding the file extension. For a given custom path, it is checked
	whether it (apparently) is an absolute or relative (to the MD2) path.
	"""
	""" get absolute skin path based on input / the one stored inside of the MD2 """
	# check box must be checked (alternatively it could be checked if the input field was empty or not ...)
	if use_custom_md2_skin:
		# an absolute path is recognized by usage of '/' (obviously not perfect detection of an absolute path)
		if os.path.isabs(custom_md2_skin_path):
			skin_path = custom_md2_skin_path
		else:
			# take everything before last '/' of MD2 path, add '/' and path of skin in same directory
			# custom_abs_path = "/".join(md2_path.split("/")[:-1]) + "/" + custom_md2_skin_path
			custom_abs_path = os.path.join(os.path.split(md2_path)[0], custom_md2_skin_path)
			print(custom_abs_path)
			skin_path = custom_abs_path
	else:
		print("stored path:", my_object.skin_names)  # unchanged path or pathes stored in the MD2

		skin_path = get_path_from_skin_name(object_path, my_object.skin_names[0])

	skin_path = get_existing_skin_path(skin_path)
	print("used skin path", skin_path)

	""" Loads required information for mesh generation and UV mapping from the .md2 file"""
	# Gets name to give to the object and mesh in the outliner
	if not displayed_name:
		object_name = "/".join(object_path.split("/")[-2:]).split(".")[:-1]
		print(object_name)
	else:
		print(displayed_name)
		object_name = [displayed_name]

	# List of vertices [x,y,z] for all frames extracted from the md2 object
	all_verts = [[x.v for x in my_object.frames[y].verts] for y in range(my_object.header.num_frames)]
	# List of vertex indices forming a triangular face
	tris = ([x.vertexIndices for x in my_object.triangles])
	# uv coordinates (in q2 terms st coordinates) for projecting the skin on the model's faces
	# blender flips images upside down when loading so v = 1-t for blender imported images
	uvs_pcx = ([(x.s, x.t) for x in my_object.texture_coordinates])
	uvs_others = ([(x.s, 1 - x.t) for x in my_object.texture_coordinates])
	# blender uv coordinate system originates at lower left

	""" Lots of code (copy and pasted) that creates a mesh and adds it to the scene collection/outlines """
	mesh = bpy.data.meshes.new(*object_name)  # add the new mesh, * extracts string from list
	obj = bpy.data.objects.new(mesh.name, mesh)
	col = bpy.data.collections.get("Collection")
	if col is None:
		col = bpy.data.collections.new("Collection")
		bpy.context.scene.collection.children.link(col)
	col.objects.link(obj)
	bpy.context.view_layer.objects.active = obj

	# Creates mesh by taking first frame's vertices and connects them via indices in tris
	mesh.from_pydata(all_verts[0], [], tris)


	""" Create animation for animated models: set keyframe for each vertex in each frame individually """
	# Create keyframes from first to last frame
	for i in range(my_object.header.num_frames):
		for idx, v in enumerate(obj.data.vertices):
			obj.data.vertices[idx].co = all_verts[i][idx]
			v.keyframe_insert('co', frame=i * 10)  # parameter index=2 restricts keyframe to dimension

	# insert first keyframe after last one to yield cyclic animation
	for idx, v in enumerate(obj.data.vertices):
		obj.data.vertices[idx].co = all_verts[0][idx]
		v.keyframe_insert('co', frame=60)

	if not skin_path:
		#ShowMessageBox("Defaulting to not assigning any material", "No skin found", "INFO")
		return {'FINISHED'}  # no idea, seems to be necessary for the UI

	if skin_path.endswith('.pcx'):
		try:
			from PIL import Image
		except ModuleNotFoundError:
			ShowMessageBox("To load .pcx skin files, see the add-on README for manual PIL installation", "Module PIL not found", "INFO")
			return {'FINISHED'}  # no idea, seems to be necessary for the UI

	""" UV Mapping: Create UV Layer, assign UV coordinates from md2 files for each face to each face's vertices """
	uv_layer = (mesh.uv_layers.new())
	mesh.uv_layers.active = uv_layer

	# add uv coordinates to each polygon (here: triangle since md2 only stores vertices and triangles)
	# note: faces and vertices are stored exactly in the order they were added
	for face_idx, face in enumerate(mesh.polygons):
		for idx, (vert_idx, loop_idx) in enumerate(zip(face.vertices, face.loop_indices)):
			if skin_path.endswith(".pcx"):
				print("PCX LOADED")
				uv_layer.data[loop_idx].uv = uvs_pcx[my_object.triangles[face_idx].textureIndices[idx]]
			else:
				uv_layer.data[loop_idx].uv = uvs_others[my_object.triangles[face_idx].textureIndices[idx]]

	""" Assign skin to mesh: Create material (barely understood copy and paste again) and set the image. 
	Might work by manually setting the textures pixels to the pixels of a PIL.Image if it would actually
	load non-empty .pcx files
	idea/TODO: Write an own pcx loader from scratch ... """
	# Creating material and corresponding notes (see Shading tab)
	mat = bpy.data.materials.new(name="md2_material")
	mat.use_nodes = True
	bsdf = mat.node_tree.nodes["Principled BSDF"]
	texImage = mat.node_tree.nodes.new('ShaderNodeTexImage')

	# if only a pcx version of the desired skin exists, load it via PIL
	# and copy pixels into the materials texture
	# otherwise use blender internal image loader (supporting .png, .jpg and .tga)
	print(f'skin_path: {skin_path}')
	if skin_path.endswith(".pcx"):
		skin = Image.open(skin_path)
		skin.load()
		skin = skin.convert("RGBA")
		skin_rgba = list(skin.getdata())
		print("important", skin_rgba[:40])
		print("path:", skin_path)
		texImage.image = bpy.data.images.new("MyImage", width=skin.size[0], height=skin.size[1])
		tmp = [y for x in skin_rgba for y in x]
		max_val = max(tmp)
		texImage.image.pixels = [x / max_val for x in tmp]
	else:
		texImage.image = bpy.data.images.load(skin_path)

		# again copy and paste
	mat.node_tree.links.new(bsdf.inputs['Base Color'], texImage.outputs['Color'])

	# Assign it to object
	if obj.data.materials:
		obj.data.materials[0] = mat
	else:
		obj.data.materials.append(mat)
	print("YAY NO ERRORS!!")
	return {'FINISHED'}  # no idea, seems to be necessary for the UI


