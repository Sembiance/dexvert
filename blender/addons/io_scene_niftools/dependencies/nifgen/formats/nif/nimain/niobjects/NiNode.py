import logging

import nifgen.formats.nif as NifFormat
from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiAVObject import NiAVObject


class NiNode(NiAVObject):

	"""
	Generic node object for grouping.
	"""

	__name__ = 'NiNode'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# The number of child objects.
		self.num_children = name_type_map['Uint'](self.context, 0, None)

		# List of child node object indices.
		self.children = Array(self.context, 0, name_type_map['NiAVObject'], (0,), name_type_map['Ref'])

		# The number of references to effect objects that follow.
		self.num_effects = name_type_map['Uint'](self.context, 0, None)

		# List of node effects. ADynamicEffect?
		self.effects = Array(self.context, 0, name_type_map['NiDynamicEffect'], (0,), name_type_map['Ref'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'num_children', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'children', Array, (0, name_type_map['NiAVObject'], (None,), name_type_map['Ref']), (False, None), (None, None)
		yield 'num_effects', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.bs_header.bs_version < 130, None)
		yield 'effects', Array, (0, name_type_map['NiDynamicEffect'], (None,), name_type_map['Ref']), (False, None), (lambda context: context.bs_header.bs_version < 130, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'num_children', name_type_map['Uint'], (0, None), (False, None)
		yield 'children', Array, (0, name_type_map['NiAVObject'], (instance.num_children,), name_type_map['Ref']), (False, None)
		if instance.context.bs_header.bs_version < 130:
			yield 'num_effects', name_type_map['Uint'], (0, None), (False, None)
			yield 'effects', Array, (0, name_type_map['NiDynamicEffect'], (instance.num_effects,), name_type_map['Ref']), (False, None)
	"""
	>>> from pyffi.formats.nif import NifFormat
	>>> x = NifFormat.NiNode()
	>>> y = NifFormat.NiNode()
	>>> z = NifFormat.NiNode()
	>>> x.num_children =1
	>>> x.children.update_size()
	>>> y in x.children
	False
	>>> x.children[0] = y
	>>> y in x.children
	True
	>>> x.add_child(z, front = True)
	>>> x.add_child(y)
	>>> x.num_children
	2
	>>> x.children[0] is z
	True
	>>> x.remove_child(y)
	>>> y in x.children
	False
	>>> x.num_children
	1
	>>> e = NifFormat.NiSpotLight()
	>>> x.add_effect(e)
	>>> x.num_effects
	1
	>>> e in x.effects
	True

	>>> from pyffi.formats.nif import NifFormat
	>>> node = NifFormat.NiNode()
	>>> child1 = NifFormat.NiNode()
	>>> child1.name = "hello"
	>>> child_2 = NifFormat.NiNode()
	>>> child_2.name = "world"
	>>> node.get_children()
	[]
	>>> node.set_children([child1, child_2])
	>>> [child.name for child in node.get_children()]
	[b'hello', b'world']
	>>> [child.name for child in node.children]
	[b'hello', b'world']
	>>> node.set_children([])
	>>> node.get_children()
	[]
	>>> # now set them the other way around
	>>> node.set_children([child_2, child1])
	>>> [child.name for child in node.get_children()]
	[b'world', b'hello']
	>>> [child.name for child in node.children]
	[b'world', b'hello']
	>>> node.remove_child(child_2)
	>>> [child.name for child in node.children]
	[b'hello']
	>>> node.add_child(child_2)
	>>> [child.name for child in node.children]
	[b'hello', b'world']

	>>> from pyffi.formats.nif import NifFormat
	>>> node = NifFormat.NiNode()
	>>> effect1 = NifFormat.NiSpotLight()
	>>> effect1.name = "hello"
	>>> effect2 = NifFormat.NiSpotLight()
	>>> effect2.name = "world"
	>>> node.get_effects()
	[]
	>>> node.set_effects([effect1, effect2])
	>>> [effect.name for effect in node.get_effects()]
	[b'hello', b'world']
	>>> [effect.name for effect in node.effects]
	[b'hello', b'world']
	>>> node.set_effects([])
	>>> node.get_effects()
	[]
	>>> # now set them the other way around
	>>> node.set_effects([effect2, effect1])
	>>> [effect.name for effect in node.get_effects()]
	[b'world', b'hello']
	>>> [effect.name for effect in node.effects]
	[b'world', b'hello']
	>>> node.remove_effect(effect2)
	>>> [effect.name for effect in node.effects]
	[b'hello']
	>>> node.add_effect(effect2)
	>>> [effect.name for effect in node.effects]
	[b'hello', b'world']
	"""
	def add_child(self, child, front=False):
		"""Add block to child list.

		:param child: The child to add.
		:type child: L{NifFormat.NiAVObject}
		:keyword front: Whether to add to the front or to the end of the
			list (default is at end).
		:type front: ``bool``
		"""
		# check if it's already a child
		if child in self.children:
			return
		# increase number of children
		num_children = self.num_children
		self.num_children = num_children + 1
		# add the child (updates size)
		self.children.append(child)
		if not front:
			return
		else:
			self.children[:] = [self.children[-1], *self.children[:-1]]

	def remove_child(self, child):
		"""Remove a block from the child list.

		:param child: The child to remove.
		:type child: L{NifFormat.NiAVObject}
		"""
		self.set_children([otherchild for otherchild in self.get_children()
						  if not(otherchild is child)])

	def get_children(self):
		"""Return a list of the children of the block.

		:return: The list of children.
		:rtype: ``list`` of L{NifFormat.NiAVObject}
		"""
		return [child for child in self.children]

	def set_children(self, childlist):
		"""Set the list of children from the given list (destroys existing list).

		:param childlist: The list of child blocks to set.
		:type childlist: ``list`` of L{NifFormat.NiAVObject}
		"""
		self.num_children = len(childlist)
		self.reset_field("children")
		for i, child in enumerate(childlist):
			self.children[i] = child

	def add_effect(self, effect):
		"""Add an effect to the list of effects.

		:param effect: The effect to add.
		:type effect: L{NifFormat.NiDynamicEffect}
		"""
		num_effs = self.num_effects
		self.num_effects = num_effs + 1
		self.effects.append(effect)

	def remove_effect(self, effect):
		"""Remove a block from the effect list.

		:param effect: The effect to remove.
		:type effect: L{NifFormat.NiDynamicEffect}
		"""
		self.set_effects([othereffect for othereffect in self.get_effects()
						 if not(othereffect is effect)])

	def get_effects(self):
		"""Return a list of the effects of the block.

		:return: The list of effects.
		:rtype: ``list`` of L{NifFormat.NiDynamicEffect}
		"""
		return [effect for effect in self.effects]

	def set_effects(self, effectlist):
		"""Set the list of effects from the given list (destroys existing list).

		:param effectlist: The list of effect blocks to set.
		:type effectlist: ``list`` of L{NifFormat.NiDynamicEffect}
		"""
		self.num_effects = len(effectlist)
		self.reset_field("effects")
		for i, effect in enumerate(effectlist):
			self.effects[i] = effect

	def merge_external_skeleton_root(self, skelroot):
		"""Attach skinned geometry to self (which will be the new skeleton root of
		the nif at the given skeleton root). Use this function if you move a
		skinned geometry from one nif into a new NIF file. The bone links will be
		updated to point to the tree at self, instead of to the external tree.
		"""
		# sanity check
		if self.name != skelroot.name:
			raise ValueError("skeleton root names do not match")

		# get a dictionary mapping bone names to bone blocks
		bone_dict = {}
		for block in self.tree():
			if isinstance(block, NifFormat.classes.NiNode):
				if block.name:
					if block.name in bone_dict:
						raise ValueError(
							"multiple NiNodes with name %s" % block.name)
					bone_dict[block.name] = block

		# add all non-bone children of the skeleton root to self
		for child in skelroot.get_children():
			# skip empty children
			if not child:
				continue
			# skip bones
			if child.name in bone_dict:
				continue
			# not a bone, so add it
			self.add_child(child)
			# fix links to skeleton root and bones
			for externalblock in child.tree():
				if isinstance(externalblock, NifFormat.classes.NiSkinInstance):
					if not(externalblock.skeleton_root is skelroot):
						raise ValueError(
							"expected skeleton root %s but got %s"
							% (skelroot.name, externalblock.skeleton_root.name))
					externalblock.skeleton_root = self
					for i, externalbone in enumerate(externalblock.bones):
						externalblock.bones[i] = bone_dict[externalbone.name]

	def merge_skeleton_roots(self):
		"""This function will look for other geometries whose skeleton
		root is a (possibly indirect) child of this node. It will then
		reparent those geometries to this node. For example, it will unify
		the skeleton roots in Morrowind's cliffracer.nif file, or of the
		(official) body skins. This makes it much easier to import
		skeletons in for instance Blender: there will be only one skeleton
		root for each bone, over all geometries.

		The merge fails for those geometries whose global skin data
		transform does not match the inverse geometry transform relative to
		the skeleton root (the maths does not work out in this case!)

		Returns list of all new blocks that have been reparented (and
		added to the skeleton root children list), and a list of blocks
		for which the merge failed.
		"""
		logger = logging.getLogger("pyffi.nif.ninode")

		result = [] # list of reparented blocks
		failed = [] # list of blocks that could not be reparented

		id44 = NifFormat.classes.Matrix44()
		id44.set_identity()

		# find the root block (direct parent of skeleton root that connects to the geometry) for each of these geometries
		for geom in self.get_global_iterator():
			# make sure we only do each geometry once
			if (geom in result) or (geom in failed):
				continue
			# only geometries
			if not isinstance(geom, NifFormat.classes.NiGeometry):
				continue
			# only skins
			if not geom.is_skin():
				continue
			# only if they have a different skeleton root
			if geom.skin_instance.skeleton_root is self:
				continue
			# check transforms
			if (geom.skin_instance.data.get_transform()
				* geom.get_transform(geom.skin_instance.skeleton_root) != id44):
				logger.warn(
					"can't rebase %s: global skin data transform does not match "
					"geometry transform relative to skeleton root" % geom.name)
				failed.append(geom)
				continue # skip this one
			# everything ok!
			# find geometry parent
			geomroot = geom.skin_instance.skeleton_root.find_chain(geom)[-2]
			# reparent
			logger.debug("detaching %s from %s" % (geom.name, geomroot.name))
			geomroot.remove_child(geom)
			logger.debug("attaching %s to %s" % (geom.name, self.name))
			self.add_child(geom)
			# set its new skeleton root
			geom.skin_instance.skeleton_root = self
			# fix transform
			geom.skin_instance.data.set_transform(
				geom.get_transform(self).get_inverse(fast=False))
			# and signal that we reparented this block
			result.append(geom)

		return result, failed

	def get_skinned_geometries(self):
		"""This function yields all skinned geometries which have self as
		skeleton root.
		"""
		for geom in self.get_global_iterator():
			if (isinstance(geom, NifFormat.classes.NiGeometry)
				and geom.is_skin()
				and geom.skin_instance.skeleton_root is self):
				yield geom

	def send_geometries_to_bind_position(self):
		"""Call this on the skeleton root of geometries. This function will
		transform the geometries, such that all skin data transforms coincide, or
		at least coincide partially.

		:return: A number quantifying the remaining difference between bind
			positions.
		:rtype: ``float``
		"""
		# get logger
		logger = logging.getLogger("generated.nif.ninode")
		# maps bone name to bind position transform matrix (relative to
		# skeleton root)
		bone_bind_transform = {}
		# find all skinned geometries with self as skeleton root
		geoms = list(self.get_skinned_geometries())
		# sort geometries by bone level
		# this ensures that "parent" geometries serve as reference for "child"
		# geometries
		sorted_geoms = []
		for bone in self.get_global_iterator():
			if not isinstance(bone, NifFormat.classes.NiNode):
				continue
			for geom in geoms:
				if not geom in sorted_geoms:
					if bone in geom.skin_instance.bones:
						sorted_geoms.append(geom)
		geoms = sorted_geoms
		# now go over all geometries and synchronize their relative bind poses
		for geom in geoms:
			skininst = geom.skin_instance
			skindata = skininst.data
			# set difference matrix to identity
			diff = NifFormat.classes.Matrix44()
			diff.set_identity()
			# go over all bones in current geometry, see if it has been visited
			# before
			for bonenode, bonedata in zip(skininst.bones, skindata.bone_list):
				# bonenode can be None; see pyffi issue #3114079
				if not bonenode:
					continue
				if bonenode.name in bone_bind_transform:
					# calculate difference
					# (see explanation below)
					diff = (bonedata.get_transform()
							* bone_bind_transform[bonenode.name]
							* geom.get_transform(self).get_inverse(fast=False))
					break

			if diff.is_identity():
				logger.debug("%s is already in bind position" % geom.name)
			else:
				logger.info("fixing %s bind position" % geom.name)
				# explanation:
				# we must set the bonedata transform T' such that its bone bind
				# position matrix
				#   T'^-1 * G
				# (where T' = the updated bonedata.get_transform()
				# and G = geom.get_transform(self))
				# coincides with the desired matrix
				#   B = bone_bind_transform[bonenode.name]
				# in other words:
				#   T' = G * B^-1
				# or, with diff = D = T * B * G^-1
				#   T' = D^-1 * T
				# to keep the geometry in sync, the vertices and normals must
				# be multiplied with D, e.g. v' = v * D
				# because the full transform
				#	v * T * ... = v * D * D^-1 * T * ... = v' * T' * ...
				# must be kept invariant
				for bonenode, bonedata in zip(skininst.bones, skindata.bone_list):
					# bonenode can be None; see pyffi issue #3114079
					logger.debug(
						"transforming bind position of bone %s"
						% bonenode.name if bonenode else "<None>")
					bonedata.set_transform(diff.get_inverse(fast=False)
										   * bonedata.get_transform())
				# transform geometry
				logger.debug("transforming vertices and normals")
				for vert in geom.data.vertices:
					newvert = vert * diff
					vert.x = newvert.x
					vert.y = newvert.y
					vert.z = newvert.z
				for norm in geom.data.normals:
					newnorm = norm * diff.get_matrix_33()
					norm.x = newnorm.x
					norm.y = newnorm.y
					norm.z = newnorm.z

			# store updated bind position for future reference
			for bonenode, bonedata in zip(skininst.bones, skindata.bone_list):
				# bonenode can be None; see pyffi issue #3114079
				if not bonenode:
					continue
				bone_bind_transform[bonenode.name] = (
					bonedata.get_transform().get_inverse(fast=False)
					* geom.get_transform(self))

		# validation: check that bones share bind position
		bone_bind_transform = {}
		error = 0.0
		for geom in geoms:
			skininst = geom.skin_instance
			skindata = skininst.data
			# go over all bones in current geometry, see if it has been visited
			# before
			for bonenode, bonedata in zip(skininst.bones, skindata.bone_list):
				if not bonenode:
					# bonenode can be None; see pyffi issue #3114079
					continue
				if bonenode.name in bone_bind_transform:
					# calculate difference
					diff = ((bonedata.get_transform().get_inverse(fast=False)
							 * geom.get_transform(self))
							- bone_bind_transform[bonenode.name])
					# calculate error (sup norm)
					error = max(error,
								max(max(abs(elem) for elem in row)
									for row in diff.as_list()))
				else:
					bone_bind_transform[bonenode.name] = (
						bonedata.get_transform().get_inverse(fast=False)
						* geom.get_transform(self))

		logger.debug("Geometry bind position error is %f" % error)
		if error > 1e-3:
			logger.warning("Failed to send some geometries to bind position")
		return error

	def send_detached_geometries_to_node_position(self):
		"""Some nifs (in particular in Morrowind) have geometries that are skinned
		but that do not share bones. In such cases, send_geometries_to_bind_position
		cannot reposition them. This function will send such geometries to the
		position of their root node.

		Examples of such nifs are the official Morrowind skins (after merging
		skeleton roots).

		Returns list of detached geometries that have been moved.
		"""
		logger = logging.getLogger("generated.nif.ninode")
		geoms = list(self.get_skinned_geometries())

		# parts the geometries into sets that do not share bone influences
		# * first construct sets of bones, merge intersecting sets
		# * then check which geometries belong to which set
		# (note: bone can be None, see issue #3114079)
		bonesets = [
			list(set(bone for bone in geom.skin_instance.bones if bone))
			for geom in geoms]
		# the merged flag signals that we are still merging bones
		merged = True
		while merged:
			merged = False
			for boneset in bonesets:
				for other_boneset in bonesets:
					# skip if sets are identical
					if other_boneset is boneset:
						continue
					# if not identical, see if they can be merged
					if set(other_boneset) & set(boneset):
						# XXX hackish but works
						# calculate union
						updated_boneset = list(set(other_boneset) | set(boneset))
						# and move all bones into one bone set
						del other_boneset[:]
						del boneset[:]
						boneset += updated_boneset
						merged = True
		# remove empty bone sets
		bonesets = list(boneset for boneset in bonesets if boneset)
		logger.debug("bones per partition are")
		for boneset in bonesets:
			logger.debug(str([bone.name for bone in boneset]))
		parts = [[geom for geom in geoms
					  if set(geom.skin_instance.bones) & set(boneset)]
					 for boneset in bonesets]
		logger.debug("geometries per partition are")
		for part in parts:
			logger.debug(str([geom.name for geom in part]))
		# if there is only one set, we are done
		if len(bonesets) <= 1:
			logger.debug("no detached geometries")
			return []

		# next, for each part, move all geometries so the lowest bone matches the
		# node transform
		for boneset, part in zip(bonesets, parts):
			logger.debug("moving part %s" % str([geom.name for geom in part]))
			# find "lowest" bone in the bone set
			lowest_dist = None
			lowest_bonenode = None
			for bonenode in boneset:
				dist = len(self.find_chain(bonenode))
				if (lowest_dist is None) or (lowest_dist > dist):
					lowest_dist = dist
					lowest_bonenode = bonenode
			logger.debug("reference bone is %s" % lowest_bonenode.name)
			# find a geometry that has this bone
			for geom in part:
				for bonenode, bonedata in zip(geom.skin_instance.bones,
											   geom.skin_instance.data.bone_list):
					if bonenode is lowest_bonenode:
						lowest_geom = geom
						lowest_bonedata = bonedata
						break
				else:
					continue
				break
			else:
				raise RuntimeError("no reference geometry with this bone: bug?")
			# calculate matrix
			diff = (lowest_bonedata.get_transform()
					* lowest_bonenode.get_transform(self)
					* lowest_geom.get_transform(self).get_inverse(fast=False))
			if diff.is_identity():
				logger.debug("%s is already in node position"
							 % lowest_bonenode.name)
				continue
			# now go over all geometries and synchronize their position to the
			# reference bone
			for geom in part:
				logger.info("moving %s to node position" % geom.name)
				# XXX we're using this trick a few times now
				# XXX move it to a separate NiGeometry function
				skininst = geom.skin_instance
				skindata = skininst.data
				# explanation:
				# we must set the bonedata transform T' such that its bone bind
				# position matrix
				#   T'^-1 * G
				# (where T' = the updated lowest_bonedata.get_transform()
				# and G = geom.get_transform(self))
				# coincides with the desired matrix
				#   B = lowest_bonenode.get_transform(self)
				# in other words:
				#   T' = G * B^-1
				# or, with diff = D = T * B * G^-1
				#   T' = D^-1 * T
				# to keep the geometry in sync, the vertices and normals must
				# be multiplied with D, e.g. v' = v * D
				# because the full transform
				#	v * T * ... = v * D * D^-1 * T * ... = v' * T' * ...
				# must be kept invariant
				for bonenode, bonedata in zip(skininst.bones, skindata.bone_list):
					logger.debug("transforming bind position of bone %s"
								 % bonenode.name)
					bonedata.set_transform(diff.get_inverse(fast=False)
										  * bonedata.get_transform())
				# transform geometry
				logger.debug("transforming vertices and normals")
				for vert in geom.data.vertices:
					newvert = vert * diff
					vert.x = newvert.x
					vert.y = newvert.y
					vert.z = newvert.z
				for norm in geom.data.normals:
					newnorm = norm * diff.get_matrix_33()
					norm.x = newnorm.x
					norm.y = newnorm.y
					norm.z = newnorm.z

	def send_bones_to_bind_position(self):
		"""This function will send all bones of geometries of this skeleton root
		to their bind position. For best results, call
		L{send_geometries_to_bind_position} first.

		:return: A number quantifying the remaining difference between bind
			positions.
		:rtype: ``float``
		"""
		# get logger
		logger = logging.getLogger("generated.nif.ninode")
		# check all bones and bone datas to see if a bind position exists
		bonelist = []
		error = 0.0
		geoms = list(self.get_skinned_geometries())
		for geom in geoms:
			skininst = geom.skin_instance
			skindata = skininst.data
			for bonenode, bonedata in zip(skininst.bones, skindata.bone_list):
				# bonenode can be None; see pyffi issue #3114079
				if not bonenode:
					continue
				# make sure all bone data of shared bones coincides
				for othergeom, otherbonenode, otherbonedata in bonelist:
					if bonenode is otherbonenode:
						diff = ((otherbonedata.get_transform().get_inverse(fast=False)
								 *
								 othergeom.get_transform(self))
								-
								(bonedata.get_transform().get_inverse(fast=False)
								 *
								 geom.get_transform(self)))
						if diff.sup_norm() > 1e-3:
							logger.warning("Geometries %s and %s do not share the same bind position: bone %s will be sent to a position matching only one of these" % (geom.name, othergeom.name, bonenode.name))
						# break the loop
						break
				else:
					# the loop did not break, so the bone was not yet added
					# add it now
					logger.debug("Found bind position data for %s" % bonenode.name)
					bonelist.append((geom, bonenode, bonedata))

		# the algorithm simply makes all transforms correct by changing
		# each local bone matrix in such a way that the global matrix
		# relative to the skeleton root matches the skinning information

		# this algorithm is numerically most stable if bones are traversed
		# in hierarchical order, so first sort the bones
		sorted_bonelist = []
		for node in self.tree():
			if not isinstance(node, NifFormat.classes.NiNode):
				continue
			for geom, bonenode, bonedata in bonelist:
				if node is bonenode:
					sorted_bonelist.append((geom, bonenode, bonedata))
		bonelist = sorted_bonelist
		# now reposition the bones
		for geom, bonenode, bonedata in bonelist:
			# explanation:
			# v * CHILD * PARENT * ...
			# = v * CHILD * DIFF^-1 * DIFF * PARENT * ...
			# and now choose DIFF such that DIFF * PARENT * ... = desired transform

			# calculate desired transform relative to skeleton root
			# transform is DIFF * PARENT
			transform = (bonedata.get_transform().get_inverse(fast=False)
						 * geom.get_transform(self))
			# calculate difference
			diff = transform * bonenode.get_transform(self).get_inverse(fast=False)
			if not diff.is_identity():
				logger.info("Sending %s to bind position"
							% bonenode.name)
				# fix transform of this node
				bonenode.set_transform(diff * bonenode.get_transform())
				# fix transform of all its children
				diff_inv = diff.get_inverse(fast=False)
				for childnode in bonenode.children:
					if childnode:
						childnode.set_transform(childnode.get_transform() * diff_inv)
			else:
				logger.debug("%s is already in bind position"
							 % bonenode.name)

		# validate
		error = 0.0
		diff_error = 0.0
		for geom in geoms:
			skininst = geom.skin_instance
			skindata = skininst.data
			# calculate geometry transform
			geomtransform = geom.get_transform(self)
			# check skin data fields (also see NiGeometry.update_bind_position)
			for i, bone in enumerate(skininst.bones):
				# bone can be None; see pyffi issue #3114079
				if bone is None:
					continue
				diff = ((skindata.bone_list[i].get_transform().get_inverse(fast=False)
						 * geomtransform)
						- bone.get_transform(self))
				# calculate error (sup norm)
				diff_error = max(max(abs(elem) for elem in row)
								 for row in diff.as_list())
				if diff_error > 1e-3:
					logger.warning(
						"Failed to set bind position of bone %s for geometry %s (error is %f)"
						% (bone.name, geom.name, diff_error))
				error = max(error, diff_error)

		logger.debug("Bone bind position maximal error is %f" % error)
		if error > 1e-3:
			logger.warning("Failed to send some bones to bind position")
		return error

