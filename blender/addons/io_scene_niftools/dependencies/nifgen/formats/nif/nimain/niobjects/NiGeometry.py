import logging
import warnings

import nifgen.formats.nif as NifFormat
from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiAVObject import NiAVObject


class NiGeometry(NiAVObject):

	"""
	Describes a visible scene element with vertices like a mesh, a particle system, lines, etc.
	Bethesda 20.2.0.7 NIFs: NiGeometry was changed to BSGeometry.
	Most new blocks (e.g. BSTriShape) do not refer to NiGeometry except NiParticleSystem was changed to use BSGeometry.
	This causes massive inheritance problems so the rows below are doubled up to exclude NiParticleSystem for Bethesda Stream 100+
	and to add data exclusive to BSGeometry.
	"""

	__name__ = 'NiGeometry'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.bounding_sphere = name_type_map['NiBound'](self.context, 0, None)
		self.bound_min_max = Array(self.context, 0, None, (0,), name_type_map['Float'])
		self.skin = name_type_map['Ref'](self.context, 0, name_type_map['NiObject'])

		# Data index (NiTriShapeData/NiTriStripData).
		self.data = name_type_map['Ref'](self.context, 0, name_type_map['NiGeometryData'])
		self.skin_instance = name_type_map['Ref'](self.context, 0, name_type_map['NiSkinInstance'])
		self.material_data = name_type_map['MaterialData'](self.context, 0, None)
		self.shader_property = name_type_map['Ref'](self.context, 0, name_type_map['BSShaderProperty'])
		self.alpha_property = name_type_map['Ref'](self.context, 0, name_type_map['NiAlphaProperty'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'bounding_sphere', name_type_map['NiBound'], (0, None), (False, None), (lambda context: 335675399 <= context.version <= 335675399 and context.bs_header.bs_version >= 100, True)
		yield 'bound_min_max', Array, (0, None, (6,), name_type_map['Float']), (False, None), (lambda context: 335675399 <= context.version <= 335675399 and context.bs_header.bs_version == 155, True)
		yield 'skin', name_type_map['Ref'], (0, name_type_map['NiObject']), (False, None), (lambda context: 335675399 <= context.version <= 335675399 and context.bs_header.bs_version >= 100, True)
		yield 'data', name_type_map['Ref'], (0, name_type_map['NiGeometryData']), (False, None), (lambda context: context.bs_header.bs_version < 100, None)
		yield 'data', name_type_map['Ref'], (0, name_type_map['NiGeometryData']), (False, None), (lambda context: 335675399 <= context.version <= 335675399 and context.bs_header.bs_version >= 100, True)
		yield 'skin_instance', name_type_map['Ref'], (0, name_type_map['NiSkinInstance']), (False, None), (lambda context: context.version >= 50528269 and context.bs_header.bs_version < 100, None)
		yield 'skin_instance', name_type_map['Ref'], (0, name_type_map['NiSkinInstance']), (False, None), (lambda context: 335675399 <= context.version <= 335675399 and context.bs_header.bs_version >= 100, True)
		yield 'material_data', name_type_map['MaterialData'], (0, None), (False, None), (lambda context: context.version >= 167772416 and context.bs_header.bs_version < 100, None)
		yield 'material_data', name_type_map['MaterialData'], (0, None), (False, None), (lambda context: 335675399 <= context.version <= 335675399 and context.bs_header.bs_version >= 100, True)
		yield 'shader_property', name_type_map['Ref'], (0, name_type_map['BSShaderProperty']), (False, None), (lambda context: 335675399 <= context.version <= 335675399 and context.bs_header.bs_version > 34, None)
		yield 'alpha_property', name_type_map['Ref'], (0, name_type_map['NiAlphaProperty']), (False, None), (lambda context: 335675399 <= context.version <= 335675399 and context.bs_header.bs_version > 34, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		if 335675399 <= instance.context.version <= 335675399 and instance.context.bs_header.bs_version >= 100 and isinstance(instance, name_type_map['NiParticleSystem']):
			yield 'bounding_sphere', name_type_map['NiBound'], (0, None), (False, None)
		if 335675399 <= instance.context.version <= 335675399 and instance.context.bs_header.bs_version == 155 and isinstance(instance, name_type_map['NiParticleSystem']):
			yield 'bound_min_max', Array, (0, None, (6,), name_type_map['Float']), (False, None)
		if 335675399 <= instance.context.version <= 335675399 and instance.context.bs_header.bs_version >= 100 and isinstance(instance, name_type_map['NiParticleSystem']):
			yield 'skin', name_type_map['Ref'], (0, name_type_map['NiObject']), (False, None)
		if instance.context.bs_header.bs_version < 100:
			yield 'data', name_type_map['Ref'], (0, name_type_map['NiGeometryData']), (False, None)
		if 335675399 <= instance.context.version <= 335675399 and instance.context.bs_header.bs_version >= 100 and not isinstance(instance, name_type_map['NiParticleSystem']):
			yield 'data', name_type_map['Ref'], (0, name_type_map['NiGeometryData']), (False, None)
		if instance.context.version >= 50528269 and instance.context.bs_header.bs_version < 100:
			yield 'skin_instance', name_type_map['Ref'], (0, name_type_map['NiSkinInstance']), (False, None)
		if 335675399 <= instance.context.version <= 335675399 and instance.context.bs_header.bs_version >= 100 and not isinstance(instance, name_type_map['NiParticleSystem']):
			yield 'skin_instance', name_type_map['Ref'], (0, name_type_map['NiSkinInstance']), (False, None)
		if instance.context.version >= 167772416 and instance.context.bs_header.bs_version < 100:
			yield 'material_data', name_type_map['MaterialData'], (0, None), (False, None)
		if 335675399 <= instance.context.version <= 335675399 and instance.context.bs_header.bs_version >= 100 and not isinstance(instance, name_type_map['NiParticleSystem']):
			yield 'material_data', name_type_map['MaterialData'], (0, None), (False, None)
		if 335675399 <= instance.context.version <= 335675399 and instance.context.bs_header.bs_version > 34:
			yield 'shader_property', name_type_map['Ref'], (0, name_type_map['BSShaderProperty']), (False, None)
			yield 'alpha_property', name_type_map['Ref'], (0, name_type_map['NiAlphaProperty']), (False, None)
	"""
	>>> from pyffi.formats.nif import NifFormat
	>>> id44 = NifFormat.Matrix44()
	>>> id44.set_identity()
	>>> skelroot = NifFormat.NiNode()
	>>> skelroot.name = 'skelroot'
	>>> skelroot.set_transform(id44)
	>>> bone1 = NifFormat.NiNode()
	>>> bone1.name = 'bone1'
	>>> bone1.set_transform(id44)
	>>> bone2 = NifFormat.NiNode()
	>>> bone2.name = 'bone2'
	>>> bone2.set_transform(id44)
	>>> bone21 = NifFormat.NiNode()
	>>> bone21.name = 'bone21'
	>>> bone21.set_transform(id44)
	>>> bone22 = NifFormat.NiNode()
	>>> bone22.name = 'bone22'
	>>> bone22.set_transform(id44)
	>>> bone211 = NifFormat.NiNode()
	>>> bone211.name = 'bone211'
	>>> bone211.set_transform(id44)
	>>> skelroot.add_child(bone1)
	>>> bone1.add_child(bone2)
	>>> bone2.add_child(bone21)
	>>> bone2.add_child(bone22)
	>>> bone21.add_child(bone211)
	>>> geom = NifFormat.NiTriShape()
	>>> geom.name = 'geom'
	>>> geom.set_transform(id44)
	>>> geomdata = NifFormat.NiTriShapeData()
	>>> skininst = NifFormat.NiSkinInstance()
	>>> skindata = NifFormat.NiSkinData()
	>>> skelroot.add_child(geom)
	>>> geom.data = geomdata
	>>> geom.skin_instance = skininst
	>>> skininst.skeleton_root = skelroot
	>>> skininst.data = skindata
	>>> skininst.num_bones = 4
	>>> skininst.bones.update_size()
	>>> skininst.bones[0] = bone1
	>>> skininst.bones[1] = bone2
	>>> skininst.bones[2] = bone22
	>>> skininst.bones[3] = bone211
	>>> skindata.num_bones = 4
	>>> skindata.bone_list.update_size()
	>>> [child.name for child in skelroot.children]
	[b'bone1', b'geom']
	>>> skindata.set_transform(id44)
	>>> for bonedata in skindata.bone_list:
	...	 bonedata.set_transform(id44)
	>>> affectedbones = geom.flatten_skin()
	>>> [bone.name for bone in affectedbones]
	[b'bone1', b'bone2', b'bone22', b'bone211']
	>>> [child.name for child in skelroot.children]
	[b'geom', b'bone1', b'bone21', b'bone2', b'bone22', b'bone211']
	"""

	def is_skin(self):
		"""Returns True if geometry is skinned."""
		return self.skin_instance != None

	def get_triangles(self):
		"""Returns the triangles that describe its mesh information, either from its data or its skin"""
		if self.is_skin():
			skin_partition = self.get_skin_partition()
			if skin_partition:
				if skin_partition.partitions:
					if skin_partition.partitions[0].has_faces:
						triangles = []
						for partition in skin_partition.partitions:
							triangles += list(partition.get_mapped_triangles())
						return triangles
		return self.data.get_triangles()

	def _validate_skin(self):
		"""Check that skinning blocks are valid. Will raise NifError exception
		if not."""
		if self.skin_instance == None: return
		if self.skin_instance.data == None:
			raise NifFormat.NifError('NiGeometry has NiSkinInstance without NiSkinData')
		if self.skin_instance.skeleton_root == None:
			raise NifFormat.NifError('NiGeometry has NiSkinInstance without skeleton root')
		if self.skin_instance.num_bones != self.skin_instance.data.num_bones:
			raise NifFormat.NifError('NiSkinInstance and NiSkinData have different number of bones')

	def add_bone(self, bone, vert_weights):
		"""Add bone with given vertex weights.
		After adding all bones, the geometry skinning information should be set
		from the current position of the bones using the L{update_bind_position} function.

		:param bone: The bone NiNode block.
		:param vert_weights: A dictionary mapping each influenced vertex index to a vertex weight."""
		self._validate_skin()
		skininst = self.skin_instance
		skindata = skininst.data
		skelroot = skininst.skeleton_root

		bone_index = skininst.num_bones
		skininst.num_bones = bone_index+1
		skininst.bones.append(bone)
		skindata.num_bones = bone_index+1
		skinbonedata = skindata.bone_list.dtype(self.context, skindata.bone_list.arg, skindata.bone_list.template)
		skindata.bone_list.append(skinbonedata)
		# set vertex weights
		skinbonedata.num_vertices = len(vert_weights)
		skinbonedata.reset_field("vertex_weights")
		for i, (vert_index, vert_weight) in enumerate(iter(vert_weights.items())):
			skinbonedata.vertex_weights[i].index = vert_index
			skinbonedata.vertex_weights[i].weight = vert_weight



	def get_vertex_weights(self):
		"""Get vertex weights in a convenient format: list bone and weight per
		vertex."""
		# shortcuts relevant blocks
		if not self.skin_instance:
			raise NifFormat.NifError('Cannot get vertex weights of geometry without skin.')
		self._validate_skin()
		geomdata = self.data
		skininst = self.skin_instance
		skindata = skininst.data
		# XXX todo: should we use list of dictionaries for this
		#		   where each dict maps bone number to the weight?
		weights = [[] for i in range(geomdata.num_vertices)]
		for bonenum, bonedata in enumerate(skindata.bone_list):
			for skinweight in bonedata.vertex_weights:
				# skip zero weights
				if skinweight.weight != 0:
					# boneweightlist is the list of (bonenum, weight) pairs that
					# we must update now
					boneweightlist = weights[skinweight.index]
					# is bonenum already in there?
					for i, (otherbonenum, otherweight) in enumerate(boneweightlist):
						if otherbonenum == bonenum:
							# yes! add the weight to the bone
							boneweightlist[i][1] += skinweight.weight
							break
					else:
						# nope... so add new [bone, weight] entry
						boneweightlist.append([bonenum, skinweight.weight])
		return weights


	def flatten_skin(self):
		"""Reposition all bone blocks and geometry block in the tree to be direct
		children of the skeleton root.

		Returns list of all used bones by the skin."""

		if not self.is_skin(): return [] # nothing to do

		result = [] # list of repositioned bones
		self._validate_skin() # validate the skin
		skininst = self.skin_instance
		skindata = skininst.data
		skelroot = skininst.skeleton_root

		# reparent geometry
		self.set_transform(self.get_transform(skelroot))
		geometry_parent = skelroot.find_chain(self, block_type = NifFormat.classes.NiAVObject)[-2]
		geometry_parent.remove_child(self) # detatch geometry from tree
		skelroot.add_child(self, front = True) # and attatch it to the skeleton root

		# reparent all the bone blocks
		for bone_block in skininst.bones:
			# skeleton root, if it is used as bone, does not need to be processed
			if bone_block == skelroot: continue
			# get bone parent
			bone_parent = skelroot.find_chain(bone_block, block_type = NifFormat.classes.NiAVObject)[-2]
			# set new child transforms
			for child in bone_block.children:
				child.set_transform(child.get_transform(bone_parent))
			# reparent children
			for child in bone_block.children:
				bone_parent.add_child(child)
			bone_block.num_children = 0
			bone_block.reset_field("children")
			# set new bone transform
			bone_block.set_transform(bone_block.get_transform(skelroot))
			# reparent bone block
			bone_parent.remove_child(bone_block)
			skelroot.add_child(bone_block)
			result.append(bone_block)

		return result



	# The nif skinning algorithm works as follows (as of nifskope):
	# v'							   # vertex after skinning in geometry space
	# = sum over {b in skininst.bones} # sum over all bones b that influence the mesh
	# weight[v][b]					 # how much bone b influences vertex v
	# * v							  # vertex before skinning in geometry space (as it is stored in the shape data)
	# * skindata.bone_list[b].transform # transform vertex to bone b space in the rest pose
	# * b.get_transform(skelroot)	   # apply animation, by multiplying with all bone matrices in the chain down to the skeleton root; the vertex is now in skeleton root space
	# * skindata.transform			 # transforms vertex from skeleton root space back to geometry space
	def get_skin_deformation(self):
		"""Returns a list of vertices and normals in their final position after
		skinning, in geometry space."""

		if not self.data: return [], []

		if not self.is_skin(): return self.data.vertices, self.data.normals

		self._validate_skin()
		skininst = self.skin_instance
		skindata = skininst.data
		skelroot = skininst.skeleton_root

		vertices = [ NifFormat.classes.Vector3() for i in range(self.data.num_vertices) ]
		normals = [ NifFormat.classes.Vector3() for i in range(self.data.num_vertices) ]
		sumweights = [ 0.0 for i in range(self.data.num_vertices) ]
		skin_offset = skindata.get_transform()
		# store one transform & rotation per bone
		bone_transforms = []
		for i, bone_block in enumerate(skininst.bones):
			bonedata = skindata.bone_list[i]
			bone_offset = bonedata.get_transform()
			bone_matrix = bone_block.get_transform(skelroot)
			transform = bone_offset * bone_matrix * skin_offset
			scale, rotation, translation = transform.get_scale_rotation_translation()
			bone_transforms.append( (transform, rotation) )
		
		# the usual case
		if skindata.has_vertex_weights:
			for i, bone_block in enumerate(skininst.bones):
				bonedata = skindata.bone_list[i]
				transform, rotation = bone_transforms[i]
				for skinweight in bonedata.vertex_weights:
					index = skinweight.index
					weight = skinweight.weight
					vertices[index] += weight * (self.data.vertices[index] * transform)
					if self.data.has_normals:
						normals[index] += weight * (self.data.normals[index] * rotation)
					sumweights[index] += weight
		# we must get weights from the partition
		else:
			skinpartition = skininst.skin_partition
			for block in skinpartition.partitions:
				# get transforms for this block
				block_bone_transforms = [bone_transforms[i] for i in block.bones]

				# go over each vert in this block
				for vert_index, vertex_weights, bone_indices in zip(block.vertex_map,
																	block.vertex_weights,
																	block.bone_indices):
					# skip verts that were already processed in an earlier block
					if sumweights[vert_index] != 0.0:
						continue
					# go over all 4 weight / bone pairs and transform this vert
					for weight, b_i in zip(vertex_weights, bone_indices):
						if weight > 0.0:
							transform, rotation = block_bone_transforms[b_i]
							vertices[vert_index] += weight * (self.data.vertices[vert_index] * transform)
							if self.data.has_normals:
								normals[vert_index] += weight * (self.data.normals[vert_index] * rotation)
							sumweights[vert_index] += weight

		for i, s in enumerate(sumweights):
			if abs(s - 1.0) > 0.01: 
				logging.getLogger("generated.nif.nigeometry").warn(
					"vertex %i has weights not summing to one" % i)

		return vertices, normals



	# ported and extended from niflib::NiNode::GoToSkeletonBindPosition() (r2518)
	def send_bones_to_bind_position(self):
		"""Send all bones to their bind position.

		@deprecated: Use L{NifFormat.NiNode.send_bones_to_bind_position} instead of
			this function.
		"""

		warnings.warn("use NifFormat.NiNode.send_bones_to_bind_position", DeprecationWarning)

		if not self.is_skin():
			return

		# validate skin and set up quick links
		self._validate_skin()
		skininst = self.skin_instance
		skindata = skininst.data
		skelroot = skininst.skeleton_root

		# reposition the bones
		for i, parent_bone in enumerate(skininst.bones):
			parent_offset = skindata.bone_list[i].get_transform()
			# if parent_bone is a child of the skeleton root, then fix its
			# transfrom
			if parent_bone in skelroot.children:
				parent_bone.set_transform(parent_offset.get_inverse() * self.get_transform(skelroot))
			# fix the transform of all its children
			for j, child_bone in enumerate(skininst.bones):
				if child_bone not in parent_bone.children: continue
				child_offset = skindata.bone_list[j].get_transform()
				child_matrix = child_offset.get_inverse() * parent_offset
				child_bone.set_transform(child_matrix)



	# ported from niflib::NiSkinData::ResetOffsets (r2561)
	def update_bind_position(self):
		"""Make current position of the bones the bind position for this geometry.

		Sets the NiSkinData overall transform to the inverse of the geometry transform
		relative to the skeleton root, and sets the NiSkinData of each bone to
		the geometry transform relative to the skeleton root times the inverse of the bone
		transform relative to the skeleton root."""
		if not self.is_skin(): return

		# validate skin and set up quick links
		self._validate_skin()
		skininst = self.skin_instance
		skindata = skininst.data
		skelroot = skininst.skeleton_root

		# calculate overall offset
		geomtransform = self.get_transform(skelroot)
		skindata.set_transform(geomtransform.get_inverse())

		# calculate bone offsets
		for i, bone in enumerate(skininst.bones):
			 skindata.bone_list[i].set_transform(geomtransform * bone.get_transform(skelroot).get_inverse())

	def get_skin_partition(self):
		"""Return the skin partition block."""
		skininst = self.skin_instance
		if not skininst:
			skinpart = None
		else:
			skinpart = skininst.skin_partition
			if not skinpart:
				skindata = skininst.data
				if skindata:
					skinpart = skindata.skin_partition

		return skinpart

	def set_skin_partition(self, skinpart):
		"""Set skin partition block."""
		skininst = self.skin_instance
		if not skininst:
			raise ValueError("Geometry has no skin instance.")

		skindata = skininst.data
		if not skindata:
			raise ValueError("Geometry has no skin data.")

		skininst.skin_partition = skinpart
		skindata.skin_partition = skinpart

