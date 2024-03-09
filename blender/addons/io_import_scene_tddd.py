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

bl_info= {
	"name": "Import Imagine/TurboSilver Objects",
	"author": "Gabriele Scibilia (<G>SZ ~ ArtNouveaU)",
	"version": (0, 1),
	"blender": (2, 80, 0),
	"location": "File > Import > Imagine/TurboSilver Object (.tddd)",
	"description": "Imports a TDDD file.",
	"warning": "",
	"wiki_url": "http://wiki.blender.org/index.php/Extensions:2.6/Py/"
				"Scripts/Import-Export/Imagine_Object",
	"category": "Import-Export",
}

__version__ = '.'.join([str(s) for s in bl_info['version']])

# Version 0.1 - September 2019
#
# Loads an Imagine/TurboSilver .TDDD object file by Impulse, Inc. (aka 3D Data Description)
#
# Notes:
#
# Imagine 3.0 Object Format, Rev 3.0 05-19-94 S.Kirvan
# http://www.ian.org/ImagineTDDDFormat.html
#
# Import LightWave Objects addon for Blender, Ken Nign
# https://github.com/sftd/blender-addons/blob/master/io_import_scene_lwo.py
#
# Updates by Gert De Roost and Dave Keeshan
# https://github.com/douglaskastle/blender-import-lwo/tree/master/io_import_scene_lwo
#
# History:
#
# 0.1 First Release for Blender Italia (www.blender.it)


import os
import struct
import chunk
import queue

import bpy
import bmesh
import mathutils
from mathutils.geometry import tessellate_polygon


#
#==================================================================================================
#     Objects - Materials - Internal classes
#==================================================================================================
#
class _obj_layer(object):
	__slots__ = (
		"name",
		"index",
		"parent",
		"pivot",
		"edges",
		"pols",
		"bones",
		"bone_names",
		"bone_rolls",
		"pnts",
		"wmaps",
		"colmaps",
		"uvmaps",
		"morphs",
		"edge_weights",
		"surf_tags",
		"has_subds",
		)
	
	def __init__(self):
		self.name= ""
		self.index= -1
		self.parent= None
		self.pivot= [0, 0, 0]
		self.edges= []
		self.pols= []
		self.bones= []
		self.bone_names= {}
		self.bone_rolls= {}
		self.pnts= []
		self.wmaps= {}
		self.colmaps= {}
		self.uvmaps= {}
		self.morphs= {}
		self.edge_weights= {}
		self.surf_tags= {}
		self.has_subds= False


class _obj_surf(object):
	__slots__ = (
		"bl_mat",
		"name",
		"source_name",
		"colr",
		"diff",
		"lumi",
		"spec",
		"hardness",
		"refl",
		"rblr",
		"tran",
		"rind",
		"tblr",
		"trnl",
		"glos",
		"shrp",
		"smooth",
		"roughness",
		)

	def __init__(self):
		self.bl_mat= None
		self.name= "Default"
		self.source_name= ""
		self.colr= [1, 1, 1]    # Color
		self.diff= 1.0          # Diffuse
		self.lumi= 0.0          # Luminosity
		self.spec= [0, 0, 0]    # Specular
		self.hardness= 0.5      # Specular Hardness
		self.refl= 0.0          # Reflectivity
		self.rblr= 0.0          # Reflection Bluring
		self.tran= 0.0          # Transparency (the opposite of Blender's Alpha value)
		self.rind= 1.0          # RT Transparency IOR
		self.tblr= 0.0          # Refraction Bluring
		self.trnl= 0.0          # Translucency
		self.glos= 0.4          # Glossiness
		self.shrp= 0.0          # Diffuse Sharpness
		self.smooth= False      # Surface Smoothing
		self.roughness= 0.4     # Roughness


#
#==================================================================================================
#     IMAGINE - 3D Data Description functions
#           Used by the Impulse's Imagine and Turbo Silver 3.0 raytracers for the Amiga.
#           TDDD files contain 3D object definitions and can be extended to describe
#           different types of object information.
#           TDDD data is stored as FORM TDDD chunks (see t3d_doc1.txt) using the Amiga and
#           Electronic Arts Interchange File Format (IFF).
#           Imagine 3.0 also supports a Texture File Format stored as a FORM TFORM chunk
#           (see t3d_doc2.txt) in an IFF file.
#==================================================================================================
#
def load_file(filename,
			  context,
			  ADD_SUBD_MOD=True,
			  LOAD_HIDDEN=False,
			  SKEL_TO_ARM=True,
			  DELETE_OBJECTS=True,
			  APPLY_MATERIALS=True
			  ):
	"""Read the TDDD file, hand off to version specific function."""
	name, ext= os.path.splitext(os.path.basename(filename))
	file= open(filename, 'rb')

	try:
		# https://docs.python.org/3/library/struct.html
		# > big-endian
		# 4s char[4]
		# 1L unsigned long (4 bytes)
		header, chunk_size, chunk_name = struct.unpack(">4s1L4s", file.read(12))
	except:
		print("Error parsing file header!")
		file.close()
		return

	layers= []
	surfs= {}
	tags= []
	# Gather the object data using the version specific handler.
	if header == b'FORM' and chunk_name == b'TDDD':
		read_tddd(file, filename, layers, surfs, tags, ADD_SUBD_MOD, LOAD_HIDDEN, SKEL_TO_ARM,)
	else:
		print("Not a supported FORM TDDD file type!")
		file.close()
		return

	file.close()

	# For debugging purpose only.
	if DELETE_OBJECTS:
		delete_objects()

	# With the data gathered, build the object(s).
	build_objects(layers, surfs, tags, name, ADD_SUBD_MOD, SKEL_TO_ARM, APPLY_MATERIALS)

	layers= None
	surfs.clear()
	tags= None


def read_tddd(file, filename, layers, surfs, tags, add_subd_mod, load_hidden, skel_to_arm):
	"""Read file, Imagine and TurboSilver."""
	handle_layer= True
	last_pols_count= 0
	just_read_bones= False
	parents= queue.LifoQueue()
	print("==================================================")
	print("TDDD Import: start importing " + filename)
	print("TDDD Version:", __version__)

	while True:
		try:
			rootchunk = chunk.Chunk(file)
		except EOFError:
			break

		if rootchunk.chunkname == b'OBJ ':
			print(" Parsing Chunk:", rootchunk.chunkname)
			surf= None
		elif rootchunk.chunkname == b'DESC':
			print(" Parsing Chunk:", rootchunk.chunkname)
			if surf != None:
				surfs[len(surfs)]= surf
			surf= _obj_surf()
			new_layr= _obj_layer()
			layers.append(new_layr)
			if parents.empty() != True:
				new_layr.parent= parents.queue[-1]
			parents.put(new_layr)
		elif rootchunk.chunkname == b'TOBJ':
			print(" Parsing Chunk:", rootchunk.chunkname)
			if surf != None:
				surfs[len(surfs)]= surf
				#surfs[surf.name]= surf
			surf= None
			if parents.empty() != True:
				parents.get()
		elif rootchunk.chunkname == b'NAME':
			print(" Parsing Chunk:", rootchunk.chunkname)
			bytes= rootchunk.read()
			name, name_len= read_lwostring(bytes[0:18])
			surf.name= name
			new_layr.name= name
			#read_name(rootchunk.read(), tags)
		elif rootchunk.chunkname == b'POSI' and handle_layer:
			read_posi(rootchunk.read(), layers)
		#elif rootchunk.chunkname == b'SIZE' and handle_layer:
		#    read_size(rootchunk.read(), layers)
		elif rootchunk.chunkname == b'PNTS' and handle_layer:
			read_pnts(rootchunk.read(), layers, 2)
		elif rootchunk.chunkname == b'PNT2' and handle_layer:
			read_pnts(rootchunk.read(), layers, 4)
		elif rootchunk.chunkname == b'EDGE' and handle_layer:
			read_edge(rootchunk.read(), layers, 2)
		elif rootchunk.chunkname == b'EDG2' and handle_layer:
			read_edge(rootchunk.read(), layers, 4)
		elif rootchunk.chunkname == b'FACE' and handle_layer:
			read_pols(rootchunk.read(), layers, 2)
		elif rootchunk.chunkname == b'FAC2' and handle_layer:
			read_pols(rootchunk.read(), layers, 4)
		elif rootchunk.chunkname == b'COLR':
			print(" Parsing Chunk:", rootchunk.chunkname)
			surf.colr= read_color255(rootchunk.read())
		elif rootchunk.chunkname == b'SPC1':
			print(" Parsing Chunk:", rootchunk.chunkname)
			surf.spec= read_color255(rootchunk.read())
		elif rootchunk.chunkname == b'PRP1' and handle_layer:
			print(" Parsing Chunk:", rootchunk.chunkname)
			read_prp1(rootchunk.read(), layers, surf)

		#==================================================
		# TODO: handle more chunks here
		#==================================================

		else:
			# For debugging purpose only
			if handle_layer:
				print("Skipping Chunk:", rootchunk.chunkname)
			rootchunk.skip()


def read_lwostring(raw_name):
	"""Parse a zero-padded string."""

	i = raw_name.find(b'\0')

	if i > 0:
		# Some plugins put non-text strings in the tags chunk.
		name = raw_name[0:i].decode("utf-8", "ignore")
		name_len = i
	else:
		name = ""
		name_len = 18

	print("\tString[%d]:" % name_len, name)

	return name, name_len


def read_color255(color_bytes):
	"""Parse the RGB color structure."""

	offset= 0
	color= struct.unpack(">BBBB", color_bytes[offset:offset+4])
	rgb= [color[1] / 255.0, color[2] / 255.0, color[3] / 255.0]

	print("\tRGB:", color[0], color[1], color[2])
 
	return rgb


def read_name(tag_bytes, object_tags):
	"""Read the object's NAME chunk."""
	offset= 0
	chunk_len= len(tag_bytes)

	#while offset < chunk_len:
	tag, tag_len= read_lwostring(tag_bytes[offset:18])
	#offset+= tag_len
	object_tags.append(tag)


def read_posi(posi_bytes, object_layers):
	"""Read the object's position (in world coordinates)."""
	print("\tReading Layer ("+object_layers[-1].name+") Position")

	posi= struct.unpack(">lll", posi_bytes[0:12])
	# Swap Y and Z to match Blender's pitch.
	posi= [posi[0] / 65536.0,
		   posi[1] / 65536.0,
		   posi[2] / 65536.0]
	object_layers[-1].pivot= posi
	print("\tPivot:", posi[0], posi[1], posi[2])


def read_size(size_bytes, object_layers):
	"""Read the object's size."""
	print("\tReading Layer ("+object_layers[-1].name+") Size")

	size= struct.unpack(">lll", size_bytes[0:12])
	# Swap Y and Z to match Blender's pitch.
	size= [size[0] / 65536.0,
		   size[1] / 65536.0,
		   size[2] / 65536.0]
	print("\tSize:", size[0], size[1], size[2])


def read_pnts(pnt_bytes, object_layers, size):
	"""Read the object's points."""
	print("\tReading Layer ("+object_layers[-1].name+") Points")
	# size= 2 for PNTS, or size= 4 for PNT2
	offset= size
	chunk_len= len(pnt_bytes)

	while offset < chunk_len:
		pnts= struct.unpack(">lll", pnt_bytes[offset:offset+12])
		offset+= 12
		# Re-order the points so that the mesh has the right pitch,
		# the pivot already has the correct order.
		pnts= [(pnts[0] / 65536.0) - object_layers[-1].pivot[0],
			   (pnts[1] / 65536.0) - object_layers[-1].pivot[1],
			   (pnts[2] / 65536.0) - object_layers[-1].pivot[2]]
		object_layers[-1].pnts.append(pnts)
		#print("\tPoint:", pnts[0], pnts[1], pnts[2])


def read_edge(edge_bytes, object_layers, size):
	"""Read the object's edges."""
	print("\tReading Layer ("+object_layers[-1].name+") Edges")
	# size= 2 for EDGE, or size= 4 for EDG2
	offset= size
	chunk_len= len(edge_bytes)

	counter= 0
	while offset < chunk_len:
		if (size == 2):
			edge= struct.unpack(">hh", edge_bytes[offset:offset+4])
		else:
			edge= struct.unpack(">ll", edge_bytes[offset:offset+8])
		offset+= 2 * size
		object_layers[-1].edges.append(edge)
		#print("\tEdge %d:" % counter, edge[0], edge[1])
		counter+= 1


def read_pols(face_bytes, object_layers, size):
	"""Read the layer's faces, each one is just a list of point indexes."""
	print("\tReading Layer ("+object_layers[-1].name+") Faces")
	# size= 2 for FACE, or size= 4 for FAC2
	offset= size
	pols_count = len(face_bytes)
	old_pols_count= len(object_layers[-1].pols)

	counter= 0
	while offset < pols_count:
		if (size == 2):
			Connects= struct.unpack(">hhh", face_bytes[offset:offset+6])
		else:
			Connects= struct.unpack(">lll", face_bytes[offset:offset+12])
		offset+= 3 * size
		all_face_pnts= []
		#print("\tFace %d:" % counter, Connects[0], Connects[1], Connects[2])
		counter+= 1

		object_layers[-1].pols.append(Connects)

	return len(object_layers[-1].pols) - old_pols_count


def read_prp1(prp1_bytes, object_layers, surf):
	"""Read the object's properties."""
	print("\tReading Layer ("+object_layers[-1].name+") Properties")

	prp1= struct.unpack(">BBBBBBBB", prp1_bytes[0:8])
	#            =  prp1[0] / 255.0         # dithering factor (0-255)
	surf.hardness=  prp1[1] / 255.0         # hardness factor (0-255)
	surf.roughness= 1.0 - (prp1[2] / 255.0) # roughness factor (0-255)
	#            =  prp1[3] / 255.0         # shinyness factor (0-255)
	#            =  prp1[4]                 # index of refraction - ir = (float)IProps[4] / 100.0 + 1.0;
	#            =  prp1[5]                 # quickdraw type: 0=none, 1=bounding box, 2=quick edges
	flag= prp1[6]                           # flag - Phong shading on/off
	if flag != 0:
		surf.smooth= True
	#            =  prp1[7]                 # flag - Genlock on/off
	print("\tHardness:", surf.hardness)
	print("\tRoughness:", surf.roughness)
	print("\tSmooth:", surf.smooth)

def build_objects(object_layers, object_surfs, object_tags, object_name, add_subd_mod, skel_to_arm, apply_materials):
	"""Using the gathered data, create the objects."""
	ob_dict= {}  # Used for the parenting setup.

	'''
	for layer_data in object_layers:
		if layer_data.parent != None:
			print(layer_data.name + " figlio di " + layer_data.parent.name)
	#error
	'''
	
	# See: https://docs.blender.org/api/current/bpy.types.Material.html
	if apply_materials:
		print("Adding %d Materials" % len(object_surfs))
		
		for surf_key in object_surfs:
			surf_data= object_surfs[surf_key]
			surf_data.bl_mat= bpy.data.materials.new(surf_data.name)
			surf_data.bl_mat.diffuse_color= (surf_data.colr[0], surf_data.colr[1], surf_data.colr[2], surf_data.diff)
			#print(surf_data.name, surf_data.colr[0]*255, surf_data.colr[1]*255, surf_data.colr[2]*255, surf_data.diff)
			#surf_data.bl_mat.diffuse_intensity= surf_data.diff
			#surf_data.bl_mat.emit= surf_data.lumi
			surf_data.bl_mat.specular_color = (surf_data.spec[0], surf_data.spec[1], surf_data.spec[2])
			surf_data.bl_mat.specular_intensity= 1.0
			#if surf_data.refl != 0.0:
			#    surf_data.bl_mat.raytrace_mirror.use= True
			#surf_data.bl_mat.raytrace_mirror.reflect_factor= surf_data.refl
			#surf_data.bl_mat.raytrace_mirror.gloss_factor= 1.0-surf_data.rblr
			#surf_data.tran=0.8
			if surf_data.tran != 0.0:
				surf_data.bl_mat.alpha_threshold= 1.0 - surf_data.tran
				surf_data.bl_mat.blend_method= 'BLEND'
			#surf_data.bl_mat.raytrace_transparency.ior= surf_data.rind
			#surf_data.bl_mat.raytrace_transparency.gloss_factor= 1.0 - surf_data.tblr
			#surf_data.bl_mat.translucency= surf_data.trnl
			#surf_data.bl_mat.specular_hardness= int(4*((10*surf_data.glos)*(10*surf_data.glos)))+4
			surf_data.bl_mat.roughness= surf_data.roughness
			# The Gloss is as close as possible given the differences.

	# Iterate over all object_layers and if any have an empty .name, set it to an incrementing number.
	for layer_data in object_layers:
		if layer_data.name == "":
			layer_data.name= "Layer " + str(layer_data.index)

	# Single layer objects use the object file's name instead.
	if len(object_layers) and object_layers[-1].name == 'Layer 1':
		print("Building '%s' Object" % object_name)
	else:
		print("Building %d Objects" % len(object_layers))

	# Before adding any meshes or armatures go into Object mode.
	if bpy.ops.object.mode_set.poll():
		bpy.ops.object.mode_set(mode='OBJECT')

	for layer_data in object_layers:
		me= bpy.data.meshes.new(layer_data.name)
		me.vertices.add(len(layer_data.pnts))
		#me.tessfaces.add(len(layer_data.pols))
		# for vi in range(len(layer_data.pnts)):
		#     me.vertices[vi].co= layer_data.pnts[vi]

		# faster, would be faster again to use an array
		me.vertices.foreach_set("co", [axis for co in layer_data.pnts for axis in co])

		ngons= {}   # To keep the FaceIdx consistent, handle NGons later.
		edges= []   # Holds the FaceIdx of the 2-point polys.

		ob= bpy.data.objects.new(layer_data.name, me)
		bpy.context.scene.collection.objects.link(ob)

		# Set [child, parent] relations.
		ob_parent= None
		if layer_data.parent != None:
			ob_parent= bpy.data.objects[layer_data.parent.name]
		ob_dict[layer_data.name] = [ob, ob_parent]

		# Move the object so the pivot is in the right place.
		ob.location= layer_data.pivot

		# Assign the material to the object displaying trans in viewport.
		if apply_materials:
			ob.active_material= bpy.data.materials.get(layer_data.name)
			ob.show_transparent= True

		# Create the Material Slots and assign the MatIndex to the correct faces.
		# Create the Vertex Groups (LW's Weight Maps).
		# Create the Shape Keys (LW's Endomorphs).
		# Create the Vertex Color maps.
		# Create the UV Maps.
		# Now add the NGons.
		# ...

		# Get a BMesh representation
		# See: https://docs.blender.org/api/current/bmesh.html
		bm = bmesh.new()    # create an empty BMesh
		bm.from_mesh(me)    # fill it in from a Mesh

		# Modify the BMesh, can do anything here...
		bm.verts.ensure_lookup_table()
		for fpol in enumerate(layer_data.pols):
			e1 = fpol[1][0]
			e2 = fpol[1][1]
			e3 = fpol[1][2]
#            print("aaaa", e1, e2, e3)
			c1 = layer_data.edges[e1]
			c2 = layer_data.edges[e2]
			c3 = layer_data.edges[e3]
#            print("bbbb", c1, c2, c3)
			vv1 = c1[0]
			vv2 = c1[1]
			vv3 = c2[0]
			vv4 = c2[1]
			if vv3 == vv1 or vv3 == vv2:
#                print("vvvv", vv1, vv2, vv4)
				face=(bm.verts[vv1], bm.verts[vv2], bm.verts[vv4])
			else:
#                print("vvvv", vv1, vv2, vv3)
				face=(bm.verts[vv3], bm.verts[vv2], bm.verts[vv1])
			try:
				bm.faces.new(face)
			except:
				pass
			
#        print("----------------", len(bm.faces))
#        print("----------------", len(bm.verts))


		# Set smooth shading
		for face in bm.faces:
			face.smooth= True

		# Recalculate normals
		bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

		# Finish up, write the bmesh back to the mesh
		bm.to_mesh(me)
		bm.free()           # free and prevent further access



		# FaceIDs are no longer a concern, so now update the mesh.
		has_edges= len(edges) > 0 or len(layer_data.edge_weights) > 0
		me.update(calc_edges=has_edges)

		# Add the edges.
		edge_offset= len(me.edges)
		me.edges.add(len(edges))
		for edge_fi in edges:
			me.edges[edge_offset].vertices[0]= layer_data.pols[edge_fi][0]
			me.edges[edge_offset].vertices[1]= layer_data.pols[edge_fi][1]
			edge_offset+= 1
			print("Edge", me.edges[edge_offset].vertices[0], me.edges[edge_offset].vertices[1])

		# Apply the Edge Weighting.
		# Unfortunately we can't exlude certain faces from the subdivision.
		# Should we build an armature from the embedded rig?

		# Clear out the dictionaries for this layer.
		layer_data.bone_names.clear()
		layer_data.bone_rolls.clear()
		layer_data.wmaps.clear()
		layer_data.colmaps.clear()
		layer_data.uvmaps.clear()
		layer_data.morphs.clear()
		layer_data.surf_tags.clear()

		# We may have some invalid mesh data, See: [#27916]
		# keep this last!
		print("Validating mesh: %r... " % me.name, end = '')
		me.validate(verbose=1)
		print("DONE!")


	# Update view layer
	layer = bpy.context.view_layer
	layer.update()

	# With the objects made, setup the parents and re-adjust the locations.
	# See: https://docs.blender.org/manual/en/latest/scene_layout/object/properties/relations/parents.html
	for ob_key in ob_dict:
		if ob_dict[ob_key][1] != None: #and ob_dict[ob_key][1] in ob_dict:
			child= ob_dict[ob_key][0]
			parent= ob_dict[ob_key][1]
			#print(child.name, "child of", parent.name)
			child.parent= parent
			child.matrix_parent_inverse= parent.matrix_world.inverted()

	print("==================================================")
	print("Done Importing TDDD File")


def delete_objects():
	try:
		# Go into Object mode.
		bpy.ops.object.mode_set(mode='OBJECT')
	except:
		pass

	# Deselect all
	bpy.ops.object.select_all(action='DESELECT')

	curves = bpy.data.curves
	
	try:
		# Select objects by type
		for o in bpy.context.scene.objects:
			if o.type == 'MESH':
				o.select_set(True)
			elif o.type == 'CURVE':
				o.select_set(True)
				cu = o.data
				curves.remove(cu)
			else:
				o.select_set(False)

		# Call the operator only once
		bpy.ops.object.delete()
	except:
		pass

	try:
		# Remove materials
		for m in bpy.data.materials:
			bpy.data.materials.remove(m)
	except:
		pass

	try:
		# Remove unused blocks
		for block in bpy.data.meshes:
			#print (block)
			if block.users == 0:
				bpy.data.meshes.remove(block)
		for block in bpy.data.materials:
			#print (block)
			if block.users == 0:
				bpy.data.materials.remove(block)
		'''
		for block in bpy.data.textures:
			if block.users == 0:
				bpy.data.textures.remove(block)
		for block in bpy.data.images:
			if block.users == 0:
				bpy.data.images.remove(block)
		'''
	except:
		pass
		
	return


#
#==================================================================================================
#     BLENDER UI Properties - IMPORT Operator
#==================================================================================================
#
from bpy.props import (
		StringProperty,
		BoolProperty,
		EnumProperty,
		IntProperty,
		FloatProperty,
		CollectionProperty,
		)


class IMPORT_OT_tddd(bpy.types.Operator):
	"""Import TDDD Operator"""
	bl_idname= "import_scene.tddd"
	bl_label= "Import TDDD"
	bl_description= "Import an Imagine/TurboSilver Object file by Impulse, Inc"
	bl_options= {'REGISTER', 'UNDO'}

	filepath: StringProperty(
		name="File Path",
		description="Filepath used for importing the TDDD file (aka 3D Data Description)",
		subtype='FILE_PATH', maxlen=1024, default="")

	filename_ext: StringProperty(
		default=".iob",
		options={'HIDDEN'})

	filter_glob: StringProperty(
		default="*.iob;*.obj;*.t3d;*.tddd",
		options={'HIDDEN'})

	DELETE_OBJECTS: BoolProperty(
		name="Import to new Scene",
		description="Creates a new scene DELETING existing objects, meshes, curves, materials",
		default=True
		)

	APPLY_MATERIALS: BoolProperty(
		name="Import and apply Materials",
		description="Loads and apply materials to objects",
		default=True
		)

	IMPORT_OBJECTS: BoolProperty(
		name="Add Objects",
		description="Custom objects have points, edges and triangles associated with them",
		default=True
		)

	IMPORT_LIGHTS: BoolProperty(
		name="Add Lights",
		description="Point and parallel light sources, round and rectangular shaped",
		default=False
		)

	IMPORT_SPHERES: BoolProperty(
		name="Add Spheres",
		description="Perfect spheres have thier radius set by the X size parameter",
		default=False
		)

	IMPORT_GROUND: BoolProperty(
		name="Add Ground",
		description="A ground object is an infinte plane",
		default=False
		)

	def draw(self, context):
		layout = self.layout
		scene = context.scene

		# Generic options
		layout.label(text="Options:")
		box = layout.box()
		sub = box.row()
		sub.prop(self, "DELETE_OBJECTS")
		sub = box.row()
		sub.prop(self, "APPLY_MATERIALS")

		# Loading/importing options
		layout.label(text="Loading Options:")
		box = layout.box()
		box.enabled = False
		sub = box.row()
		sub.prop(self, "IMPORT_OBJECTS")
		sub.enabled = False
		sub = box.row()
		sub.prop(self, "IMPORT_LIGHTS")
		sub = box.row()
		sub.prop(self, "IMPORT_SPHERES")
		sub = box.row()
		sub.prop(self, "IMPORT_GROUND")

	def execute(self, context):
		load_file(self.filepath,
				 context,
				 True,          #self.ADD_SUBD_MOD,
				 False,         #self.LOAD_HIDDEN,
				 True,          #self.SKEL_TO_ARM,
				 self.DELETE_OBJECTS,
				 self.APPLY_MATERIALS
				 )
		return {'FINISHED'}

	def invoke(self, context, event):
		wm= context.window_manager
		wm.fileselect_add(self)
		return {'RUNNING_MODAL'}


#
#==================================================================================================
#     Register - Unregister - MAIN
#==================================================================================================
#
def menu_func(self, context):
	self.layout.operator(IMPORT_OT_tddd.bl_idname, text="Impulse, Inc. 3D Data Description")

def register():
	bpy.utils.register_class(IMPORT_OT_tddd)

	# The INFO_MT_file_export has been moved to TOPBAR_MT_file_export.
	bpy.types.TOPBAR_MT_file_import.append(menu_func)


def unregister():
	bpy.utils.unregister_class(IMPORT_OT_tddd)

	# The INFO_MT_file_export has been moved to TOPBAR_MT_file_export.
	bpy.types.TOPBAR_MT_file_import.remove(menu_func)


if __name__ == "__main__":
	register()

	# Test call
	#bpy.ops.import_scene.tddd('INVOKE_DEFAULT')
	#bpy.types.TOPBAR_MT_file_import.remove(menu_func)
