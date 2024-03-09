from itertools import repeat
import logging
import struct
import warnings

import nifgen.formats.nif as NifFormat
from nifgen.utils.vertex_cache import get_cache_optimized_triangles, stable_stripify
from nifgen.formats.nif.nimain.niobjects.NiGeometry import NiGeometry


class NiTriBasedGeom(NiGeometry):

	"""
	Describes a mesh, built from triangles.
	"""

	__name__ = 'NiTriBasedGeom'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
	def get_tangent_space(self):
		"""Return iterator over normal, tangent, bitangent vectors.
		If the block has no tangent space, then returns None.
		"""

		def bytes2vectors(data, pos, num):
			for i in range(num):
				vec = NifFormat.classes.Vector3()
				# XXX _byte_order! assuming little endian
				vec.x, vec.y, vec.z = struct.unpack('<fff',
													data[pos:pos+12])
				yield vec
				pos += 12


		if self.data.num_vertices == 0:
			return ()

		if not self.data.normals:
			#raise ValueError('geometry has no normals')
			return None

		if (not self.data.tangents) or (not self.data.bitangents):
			# no tangents and bitangents at the usual location
			# perhaps there is Oblivion style data?
			for extra in self.get_extra_datas():
				if isinstance(extra, NifFormat.classes.NiBinaryExtraData):
					if extra.name == b'Tangent space (binormal & tangent vectors)':
						break
			else:
				#raise ValueError('geometry has no tangents')
				return None
			if 24 * self.data.num_vertices != len(extra.binary_data):
				raise ValueError(
					'tangent space data has invalid size, expected %i bytes but got %i'
					% (24 * self.data.num_vertices, len(extra.binary_data)))
			tangents = bytes2vectors(extra.binary_data,
									 0,
									 self.data.num_vertices)
			bitangents = bytes2vectors(extra.binary_data,
									   12 * self.data.num_vertices,
									   self.data.num_vertices)
		else:
			tangents = self.data.tangents
			bitangents = self.data.bitangents

		return zip(self.data.normals, tangents, bitangents)

	def update_tangent_space(self, as_extra=None, vertexprecision=3, normalprecision=3, uvprecision=3):
		"""Recalculate tangent space data.

		:param as_extra: Whether to store the tangent space data as extra data
			(as in Oblivion) or not (as in Fallout 3). If not set, switches to
			Oblivion if an extra data block is found, otherwise does default.
			Set it to override this detection (for example when using this
			function to create tangent space data) and force behaviour.
		"""
		# check that self.data exists and is valid
		if not isinstance(self.data, NifFormat.classes.NiTriBasedGeomData):
			raise ValueError('cannot update tangent space of a geometry with %s data'
							 %(self.data.__class__ if self.data else 'no'))

		verts = self.data.vertices
		norms = self.data.normals
		if len(self.data.uv_sets) > 0:
			uvs = self.data.uv_sets[0]
		else:
			# This is an error state and the mesh part should not be included in the exported nif.
			# happens in Fallout NV meshes/architecture/bouldercity/arcadeendl.nif
			self.data.extra_vectors_flags = 0
			warnings.warn("Attempting to export mesh without uv data", DeprecationWarning)
			return

		# check that shape has norms and uvs
		if len(uvs) == 0 or len(norms) == 0: return

		# identify identical (vertex, normal) pairs to avoid issues along
		# uv seams due to vertex duplication
		# implementation note: uvprecision and vcolprecision 0
		# should be enough, but use -2 just to be really sure
		# that this is ignored
		v_hash_map = list(
			self.data.get_vertex_hash_generator(
				vertexprecision=vertexprecision,
				normalprecision=normalprecision,
				uvprecision=uvprecision,
				vcolprecision=-2))

		# tangent and binormal dictionaries by vertex hash
		bin = dict((h, NifFormat.classes.Vector3()) for h in v_hash_map)
		tan = dict((h, NifFormat.classes.Vector3()) for h in v_hash_map)

		# calculate tangents and binormals from vertex and texture coordinates
		for t1, t2, t3 in self.data.get_triangles():
			# find hash values
			h1 = v_hash_map[t1]
			h2 = v_hash_map[t2]
			h3 = v_hash_map[t3]
			# skip degenerate triangles
			if h1 == h2 or h2 == h3 or h3 == h1:
				continue

			v_1 = verts[t1]
			v_2 = verts[t2]
			v_3 = verts[t3]
			w1 = uvs[t1]
			w2 = uvs[t2]
			w3 = uvs[t3]
			v_2v_1 = v_2 - v_1
			v_3v_1 = v_3 - v_1
			w2w1 = w2 - w1
			w3w1 = w3 - w1

			# surface of triangle in texture space
			r = w2w1.u * w3w1.v - w3w1.u * w2w1.v

			# sign of surface
			r_sign = (1 if r >= 0 else -1)

			# contribution of this triangle to tangents and binormals
			sdir = NifFormat.classes.Vector3()
			sdir.x = (w3w1.v * v_2v_1.x - w2w1.v * v_3v_1.x) * r_sign
			sdir.y = (w3w1.v * v_2v_1.y - w2w1.v * v_3v_1.y) * r_sign
			sdir.z = (w3w1.v * v_2v_1.z - w2w1.v * v_3v_1.z) * r_sign
			try:
				sdir.normalize()
			except ZeroDivisionError: # catches zero vector
				continue # skip triangle
			except ValueError: # catches invalid data
				continue # skip triangle

			tdir = NifFormat.classes.Vector3()
			tdir.x = (w2w1.u * v_3v_1.x - w3w1.u * v_2v_1.x) * r_sign
			tdir.y = (w2w1.u * v_3v_1.y - w3w1.u * v_2v_1.y) * r_sign
			tdir.z = (w2w1.u * v_3v_1.z - w3w1.u * v_2v_1.z) * r_sign
			try:
				tdir.normalize()
			except ZeroDivisionError: # catches zero vector
				continue # skip triangle
			except ValueError: # catches invalid data
				continue # skip triangle

			# vector combination algorithm could possibly be improved
			for h in [h1, h2, h3]:
				# addition inlined for speed
				tanh = tan[h]
				tanh.x += tdir.x
				tanh.y += tdir.y
				tanh.z += tdir.z
				binh = bin[h]
				binh.x += sdir.x
				binh.y += sdir.y
				binh.z += sdir.z

		xvec = NifFormat.classes.Vector3()
		xvec.x = 1.0
		xvec.y = 0.0
		xvec.z = 0.0
		yvec = NifFormat.classes.Vector3()
		yvec.x = 0.0
		yvec.y = 1.0
		yvec.z = 0.0
		for n, h in zip(norms, v_hash_map):
			binh = bin[h]
			tanh = tan[h]
			try:
				n.normalize()
			except (ValueError, ZeroDivisionError):
				# this happens if the normal has NAN values or is zero
				# just pick something in that case
				n = yvec
			try:
				# turn n, bin, tan into a base via Gram-Schmidt
				# bin[h] -= n * (n * bin[h])
				# inlined for speed
				scalar = n * binh
				binh.x -= n.x * scalar
				binh.y -= n.y * scalar
				binh.z -= n.z * scalar
				binh.normalize()

				# tan[h] -= n * (n * tan[h])
				# tan[h] -= bin[h] * (bin[h] * tan[h])
				# inlined for speed
				scalar = n * tanh
				tanh.x -= n.x * scalar
				tanh.y -= n.y * scalar
				tanh.z -= n.z * scalar
				
				scalar = binh * tanh
				tanh.x -= binh.x * scalar
				tanh.y -= binh.y * scalar
				tanh.z -= binh.z * scalar
				tanh.normalize()
			except ZeroDivisionError:
				# insuffient data to set tangent space for this vertex
				# in that case pick a space
				binh = xvec.crossproduct(n)
				try:
					binh.normalize()
				except ZeroDivisionError:
					binh = yvec.crossproduct(n)
					binh.normalize() # should work now
				tanh = n.crossproduct(binh)

		# tangent and binormal lists by vertex index
		tan = [tan[h] for h in v_hash_map]
		bin = [bin[h] for h in v_hash_map]

		# find possible extra data block
		for extra in self.get_extra_datas():
			if isinstance(extra, NifFormat.classes.NiBinaryExtraData):
				if extra.name == b'Tangent space (binormal & tangent vectors)':
					break
		else:
			extra = None

		# if autodetection is on, do as_extra only if an extra data block is found
		if as_extra is None:
			if extra:
				as_extra = True
			else:
				as_extra = False

		if as_extra:
			# if tangent space extra data already exists, use it
			if not extra:
				# otherwise, create a new block and link it
				extra = NifFormat.classes.NiBinaryExtraData()
				extra.name = b'Tangent space (binormal & tangent vectors)'
				self.add_extra_data(extra)

			# write the data
			binarydata = bytearray()
			for vec in tan + bin:
				# XXX _byte_order!! assuming little endian
				binarydata += struct.pack('<fff', vec.x, vec.y, vec.z)
			extra.binary_data = bytes(binarydata)
		else:
			# set tangent space flag
			self.data.extra_vectors_flags = 16
			# XXX used to be 61440
			# XXX from Sid Meier's Railroad
			self.data.reset_field("tangents")
			self.data.reset_field("bitangents")
			for vec, data_tans in zip(tan, self.data.tangents):
				data_tans.x = vec.x
				data_tans.y = vec.y
				data_tans.z = vec.z
			for vec, data_bins in zip(bin, self.data.bitangents):
				data_bins.x = vec.x
				data_bins.y = vec.y
				data_bins.z = vec.z
				
			

	# ported from nifskope/skeleton.cpp:spSkinPartition
	def update_skin_partition(self,
							maxbonesperpartition=4, maxbonespervertex=4,
							verbose=0, stripify=True, stitchstrips=False,
							padbones=False,
							triangles=None, trianglepartmap=None,
							maximize_bone_sharing=False):
		"""Recalculate skin partition data.

		:deprecated: Do not use the verbose argument.
		:param maxbonesperpartition: Maximum number of bones in each partition.
			The num_bones field will not exceed this number.
		:param maxbonespervertex: Maximum number of bones per vertex.
			The num_weights_per_vertex field will be exactly equal to this number.
		:param verbose: Ignored, and deprecated. Set pyffi's log level instead.
		:param stripify: If true, stripify the partitions, otherwise use triangles.
		:param stitchstrips: If stripify is true, then set this to true to stitch
			the strips.
		:param padbones: Enforces the numbones field to be equal to
			maxbonesperpartition. Also ensures that the bone indices are unique
			and sorted, per vertex. Raises an exception if maxbonespervertex
			is not equal to maxbonesperpartition (in that case bone indices cannot
			be unique and sorted). This options is required for Freedom Force vs.
			the 3rd Reich skin partitions.
		:param triangles: The triangles of the partition (if not specified, then
			this defaults to C{self.data.get_triangles()}.
		:param trianglepartmap: Maps each triangle to a partition index. Faces with
			different indices will never appear in the same partition. If the skin
			instance is a BSDismemberSkinInstance, then these indices are used as
			body part types, and the partitions in the BSDismemberSkinInstance are
			updated accordingly. Note that the faces are counted relative to
			L{triangles}.
		:param maximize_bone_sharing: Maximize bone sharing between partitions.
			This option is useful for Fallout 3.
		"""
		logger = logging.getLogger("generated.nif.nitribasedgeom")

		# if trianglepartmap not specified, map everything to index 0
		if trianglepartmap is None:
			trianglepartmap = repeat(0)

		# shortcuts relevant blocks
		if not self.skin_instance:
			# no skin, nothing to do
			return
		self._validate_skin()
		geomdata = self.data
		skininst = self.skin_instance
		skindata = skininst.data

		# get skindata vertex weights
		logger.debug("Getting vertex weights.")
		weights = self.get_vertex_weights()

		# count minimum and maximum number of bones per vertex
		minbones = min(len(weight) for weight in weights)
		maxbones = max(len(weight) for weight in weights)
		if minbones <= 0:
			noweights = [v for v, weight in enumerate(weights)
						 if not weight]
			#raise ValueError(
			logger.warn(
				'bad NiSkinData: some vertices have no weights %s'
				% noweights)
		logger.info("Counted minimum of %i and maximum of %i bones per vertex"
					% (minbones, maxbones))

		# reduce bone influences to meet maximum number of bones per vertex
		logger.info("Imposing maximum of %i bones per vertex." % maxbonespervertex)
		lostweight = 0.0
		for weight in weights:
			if len(weight) > maxbonespervertex:
				# delete bone influences with least weight
				weight.sort(key=lambda x: x[1], reverse=True) # sort by weight
				# save lost weight to return to user
				lostweight = max(
					lostweight, max(
						[x[1] for x in weight[maxbonespervertex:]]))
				del weight[maxbonespervertex:] # only keep first elements
				# normalize
				totalweight = sum([x[1] for x in weight]) # sum of all weights
				for x in weight: x[1] /= totalweight
				maxbones = maxbonespervertex
			# sort by again by bone (relied on later when matching vertices)
			weight.sort(key=lambda x: x[0])

		# reduce bone influences to meet maximum number of bones per partition
		# (i.e. maximum number of bones per triangle)
		logger.info(
			"Imposing maximum of %i bones per triangle (and hence, per partition)."
			% maxbonesperpartition)

		if triangles is None:
			triangles = geomdata.get_triangles()

		for tri in triangles:
			while True:
				# find the bones influencing this triangle
				tribones = []
				for t in tri:
					tribones.extend([bonenum for bonenum, boneweight in weights[t]])
				tribones = set(tribones)
				# target met?
				if len(tribones) <= maxbonesperpartition:
					break
				# no, need to remove a bone

				# sum weights for each bone to find the one that least influences
				# this triangle
				tribonesweights = {}
				for bonenum in tribones: tribonesweights[bonenum] = 0.0
				nono = set() # bones with weight 1 cannot be removed
				for skinweights in [weights[t] for t in tri]:
					# skinweights[0] is the first skinweight influencing vertex t
					# and skinweights[0][0] is the bone number of that bone
					if len(skinweights) == 1: nono.add(skinweights[0][0])
					for bonenum, boneweight in skinweights:
						tribonesweights[bonenum] += boneweight

				# select a bone to remove
				# first find bones we can remove

				# restrict to bones not in the nono set
				tribonesweights = [
					x for x in list(tribonesweights.items()) if x[0] not in nono]
				if not tribonesweights:
					raise ValueError(
						"cannot remove anymore bones in this skin; "
						"increase maxbonesperpartition and try again")
				# sort by vertex weight sum the last element of this list is now a
				# candidate for removal
				tribonesweights.sort(key=lambda x: x[1], reverse=True)
				minbone = tribonesweights[-1][0]

				# remove minbone from all vertices of this triangle and from all
				# matching vertices
				for t in tri:
					for tt in [t]: #match[t]:
						# remove bone
						weight = weights[tt]
						for i, (bonenum, boneweight) in enumerate(weight):
							if bonenum == minbone:
								# save lost weight to return to user
								lostweight = max(lostweight, boneweight)
								del weight[i]
								break
						else:
							continue
						# normalize
						totalweight = sum([x[1] for x in weight])
						for x in weight:
							x[1] /= totalweight

		# split triangles into partitions
		logger.info("Creating partitions")
		parts = []
		# keep creating partitions as long as there are triangles left
		while triangles:
			# create a partition
			part = [set(), [], None] # bones, triangles, partition index
			usedverts = set()
			addtriangles = True
			# keep adding triangles to it as long as the flag is set
			while addtriangles:
				# newtriangles is a list of triangles that have not been added to
				# the partition, similar for newtrianglepartmap
				newtriangles = []
				newtrianglepartmap = []
				for tri, partindex in zip(triangles, trianglepartmap):
					# find the bones influencing this triangle
					tribones = []
					for t in tri:
						tribones.extend([
							bonenum for bonenum, boneweight in weights[t]])
					tribones = set(tribones)
					# if part has no bones,
					# or if part has all bones of tribones and index coincides
					# then add this triangle to this part
					if ((not part[0])
						or ((part[0] >= tribones) and (part[2] == partindex))):
						part[0] |= tribones
						part[1].append(tri)
						usedverts |= set(tri)
						# if part was empty, assign it the index
						if part[2] is None:
							part[2] = partindex
					else:
						newtriangles.append(tri)
						newtrianglepartmap.append(partindex)
				triangles = newtriangles
				trianglepartmap = newtrianglepartmap

				# if we have room left in the partition
				# then add adjacent triangles
				addtriangles = False
				newtriangles = []
				newtrianglepartmap = []
				if len(part[0]) < maxbonesperpartition:
					for tri, partindex in zip(triangles, trianglepartmap):
						# if triangle is adjacent, and has same index
						# then check if it can be added to the partition
						if (usedverts & set(tri)) and (part[2] == partindex):
							# find the bones influencing this triangle
							tribones = []
							for t in tri:
								tribones.extend([
									bonenum for bonenum, boneweight in weights[t]])
							tribones = set(tribones)
							# and check if we exceed the maximum number of allowed
							# bones
							if len(part[0] | tribones) <= maxbonesperpartition:
								part[0] |= tribones
								part[1].append(tri)
								usedverts |= set(tri)
								# signal another try in adding triangles to
								# the partition
								addtriangles = True
							else:
								newtriangles.append(tri)
								newtrianglepartmap.append(partindex)
						else:
							newtriangles.append(tri)
							newtrianglepartmap.append(partindex)
					triangles = newtriangles
					trianglepartmap = newtrianglepartmap

			parts.append(part)

		logger.info("Created %i small partitions." % len(parts))

		# merge all partitions
		logger.info("Merging partitions.")
		merged = True # signals success, in which case do another run
		while merged:
			merged = False
			# newparts is to contain the updated merged partitions as we go
			newparts = []
			# addedparts is the set of all partitions from parts that have been
			# added to newparts
			addedparts = set()
			# try all combinations
			for a, parta in enumerate(parts):
				if a in addedparts:
					continue
				newparts.append(parta)
				addedparts.add(a)
				for b, partb in enumerate(parts):
					if b <= a:
						continue
					if b in addedparts:
						continue
					# if partition indices are the same, and bone limit is not
					# exceeded, merge them
					if ((parta[2] == partb[2])
						and (len(parta[0] | partb[0]) <= maxbonesperpartition)):
						parta[0] |= partb[0]
						parta[1] += partb[1]
						addedparts.add(b)
						merged = True # signal another try in merging partitions
			# update partitions to the merged partitions
			parts = newparts

		# write the NiSkinPartition
		logger.info("Skin has %i partitions." % len(parts))

		# if skin partition already exists, use it
		if skindata.skin_partition != None:
			skinpart = skindata.skin_partition
			skininst.skin_partition = skinpart
		elif skininst.skin_partition != None:
			skinpart = skininst.skin_partition
			skindata.skin_partition = skinpart
		else:
		# otherwise, create a new block and link it
			skinpart = NifFormat.classes.NiSkinPartition()
			skindata.skin_partition = skinpart
			skininst.skin_partition = skinpart

		# set number of partitions
		skinpart.num_partitions = len(parts)
		skinpart.reset_field("partitions")

		# maximize bone sharing, if requested
		if maximize_bone_sharing:
			logger.info("Maximizing shared bones.")
			# new list of partitions, sorted to maximize bone sharing
			newparts = []
			# as long as there are parts to add
			while parts:
				# current set of partitions with shared bones
				# starts a new set of partitions with shared bones
				sharedparts = [parts.pop()]
				sharedboneset = sharedparts[0][0]
				# go over all other partitions, and try to add them with
				# shared bones
				oldparts = parts[:]
				parts = []
				for otherpart in oldparts:
					# check if bones can be added
					if len(sharedboneset | otherpart[0]) <= maxbonesperpartition:
						# ok, we can share bones!
						# update set of shared bones
						sharedboneset |= otherpart[0]
						# add this other partition to list of shared parts
						sharedparts.append(otherpart)
						# update bone set in all shared parts
						for sharedpart in sharedparts:
							sharedpart[0] = sharedboneset
					else:
						# not added to sharedparts,
						# so we must keep it for the next iteration
						parts.append(otherpart)
				# update list of partitions
				newparts.extend(sharedparts)

			# store update
			parts = newparts

		# for Fallout 3, set dismember partition indices
		if isinstance(skininst, NifFormat.classes.BSDismemberSkinInstance):
			skininst.num_partitions = len(parts)
			skininst.reset_field("partitions")
			lastpart = None
			for bodypart, part in zip(skininst.partitions, parts):
				bodypart.body_part = part[2]
				if (lastpart is None) or (lastpart[0] != part[0]):
					# start new bone set, if bones are not shared
					bodypart.part_flag.start_new_boneset = 1
				else:
					# do not start new bone set
					bodypart.part_flag.start_new_boneset = 0
				# caps are invisible
				bodypart.part_flag.editor_visible = (part[2] < 100
													 or part[2] >= 1000)
				# store part for next iteration
				lastpart = part

		for skinpartblock, part in zip(skinpart.partitions, parts):
			# get sorted list of bones
			bones = sorted(list(part[0]))
			triangles = part[1]
			logger.info("Optimizing triangle ordering in partition %i"
						% parts.index(part))
			# optimize triangles for vertex cache and calculate strips
			triangles = get_cache_optimized_triangles(
				triangles)
			strips = stable_stripify(
				triangles, stitchstrips=stitchstrips)
			triangles_size = 3 * len(triangles)
			strips_size = len(strips) + sum(len(strip) for strip in strips)
			vertices = []
			# decide whether to use strip or triangles as primitive
			if stripify is None:
				stripifyblock = (
					strips_size < triangles_size
					and all(len(strip) < 65536 for strip in strips))
			else:
				stripifyblock = stripify
			if stripifyblock:
				# stripify the triangles
				# also update triangle list
				numtriangles = 0
				# calculate number of triangles and get sorted
				# list of vertices
				# for optimal performance, vertices must be sorted
				# by strip
				for strip in strips:
					numtriangles += len(strip) - 2
					for t in strip:
						if t not in vertices:
							vertices.append(t)
			else:
				numtriangles = len(triangles)
				# get sorted list of vertices
				# for optimal performance, vertices must be sorted
				# by triangle
				for tri in triangles:
					for t in tri:
						if t not in vertices:
							vertices.append(t)
			# set all the data
			skinpartblock.num_vertices = len(vertices)
			skinpartblock.num_triangles = numtriangles
			if not padbones:
				skinpartblock.num_bones = len(bones)
			else:
				if maxbonesperpartition != maxbonespervertex:
					raise ValueError(
						"when padding bones maxbonesperpartition must be "
						"equal to maxbonespervertex")
				# freedom force vs. the 3rd reich needs exactly 4 bones per
				# partition on every partition block
				skinpartblock.num_bones = maxbonesperpartition
			if stripifyblock:
				skinpartblock.num_strips = len(strips)
			else:
				skinpartblock.num_strips = 0
			# maxbones would be enough as num_weights_per_vertex but the Gamebryo
			# engine doesn't like that, it seems to want exactly 4 even if there
			# are fewer
			skinpartblock.num_weights_per_vertex = maxbonespervertex
			skinpartblock.reset_field("bones")
			for i, bonenum in enumerate(bones):
				skinpartblock.bones[i] = bonenum
			for i in range(len(bones), skinpartblock.num_bones):
				skinpartblock.bones[i] = 0 # dummy bone slots refer to first bone
			skinpartblock.has_vertex_map = True
			skinpartblock.reset_field("vertex_map")
			for i, v in enumerate(vertices):
				skinpartblock.vertex_map[i] = v
			skinpartblock.has_vertex_weights = True
			skinpartblock.reset_field("vertex_weights")
			for i, v in enumerate(vertices):
				for j in range(skinpartblock.num_weights_per_vertex):
					if j < len(weights[v]):
						skinpartblock.vertex_weights[i][j] = weights[v][j][1]
					else:
						skinpartblock.vertex_weights[i][j] = 0.0
			if stripifyblock:
				skinpartblock.has_faces = True
				skinpartblock.reset_field("strip_lengths")
				for i, strip in enumerate(strips):
					skinpartblock.strip_lengths[i] = len(strip)
				skinpartblock.reset_field("strips")
				for i, strip in enumerate(strips):
					for j, v in enumerate(strip):
						skinpartblock.strips[i][j] = vertices.index(v)
			else:
				skinpartblock.has_faces = True
				# clear strip lengths array
				skinpartblock.reset_field("strip_lengths")
				# clear strips array
				skinpartblock.reset_field("strips")
				skinpartblock.reset_field("triangles")
				for i, (v_1,v_2,v_3) in enumerate(triangles):
					skinpartblock.triangles[i].v_1 = vertices.index(v_1)
					skinpartblock.triangles[i].v_2 = vertices.index(v_2)
					skinpartblock.triangles[i].v_3 = vertices.index(v_3)
			skinpartblock.has_bone_indices = True
			skinpartblock.reset_field("bone_indices")
			for i, v in enumerate(vertices):
				# the boneindices set keeps track of indices that have not been
				# used yet
				boneindices = set(range(skinpartblock.num_bones))
				for j in range(len(weights[v])):
					skinpartblock.bone_indices[i][j] = bones.index(weights[v][j][0])
					boneindices.remove(skinpartblock.bone_indices[i][j])
				for j in range(len(weights[v]),skinpartblock.num_weights_per_vertex):
					if padbones:
						# if padbones is True then we have enforced
						# num_bones == num_weights_per_vertex so this will not trigger
						# a KeyError
						skinpartblock.bone_indices[i][j] = boneindices.pop()
					else:
						skinpartblock.bone_indices[i][j] = 0

			# sort weights
			for i, v in enumerate(vertices):
				vweights = []
				for j in range(skinpartblock.num_weights_per_vertex):
					vweights.append([
						skinpartblock.bone_indices[i][j],
						skinpartblock.vertex_weights[i][j]])
				if padbones:
					# by bone index (for ffvt3r)
					vweights.sort(key=lambda w: w[0])
				else:
					# by weight (for fallout 3, largest weight first)
					vweights.sort(key=lambda w: -w[1])
				for j in range(skinpartblock.num_weights_per_vertex):
					skinpartblock.bone_indices[i][j] = vweights[j][0]
					skinpartblock.vertex_weights[i][j] = vweights[j][1]

		return lostweight

	# ported from nifskope/skeleton.cpp:spFixBoneBounds
	def update_skin_center_radius(self):
		"""Update centers and radii of all skin data fields."""
		# shortcuts relevant blocks
		if not self.skin_instance:
			return # no skin, nothing to do
		self._validate_skin()
		geomdata = self.data
		skininst = self.skin_instance
		skindata = skininst.data

		verts = geomdata.vertices

		for skindatablock in skindata.bone_list:
			# find all vertices influenced by this bone
			boneverts = [verts[skinweight.index]
						 for skinweight in skindatablock.vertex_weights]

			# find bounding box of these vertices
			low = NifFormat.classes.Vector3()
			low.x = min(v.x for v in boneverts)
			low.y = min(v.y for v in boneverts)
			low.z = min(v.z for v in boneverts)

			high = NifFormat.classes.Vector3()
			high.x = max(v.x for v in boneverts)
			high.y = max(v.y for v in boneverts)
			high.z = max(v.z for v in boneverts)

			# center is in the center of the bounding box
			center = (low + high) * 0.5

			# radius is the largest distance from the center
			r2 = 0.0
			for v in boneverts:
				d = center - v
				r2 = max(r2, d.x*d.x+d.y*d.y+d.z*d.z)
			radius = r2 ** 0.5

			# transform center in proper coordinates (radius remains unaffected)
			center *= skindatablock.get_transform()

			# save data
			skindatablock.bounding_sphere.center.x = center.x
			skindatablock.bounding_sphere.center.y = center.y
			skindatablock.bounding_sphere.center.z = center.z
			skindatablock.bounding_sphere.radius = radius

	def get_interchangeable_tri_shape(self, triangles=None):
		"""Returns a NiTriShape block that is geometrically
		interchangeable. If you do not want to set the triangles
		from the original shape, use the triangles argument.
		"""
		# copy the shape (first to NiTriBasedGeom and then to NiTriShape)
		shape = NifFormat.classes.NiTriShape().deepcopy(
			NifFormat.classes.NiTriBasedGeom().deepcopy(self))
		# copy the geometry without strips
		shapedata = NifFormat.classes.NiTriShapeData().deepcopy(
			NifFormat.classes.NiTriBasedGeomData().deepcopy(self.data))
		# update the shape data
		if triangles is None:
			shapedata.set_triangles(self.data.get_triangles())
		else:
			shapedata.set_triangles(triangles)
		# relink the shape data
		shape.data = shapedata
		# and return the result
		return shape

	def get_interchangeable_tri_strips(self, strips=None):
		"""Returns a NiTriStrips block that is geometrically
		interchangeable.  If you do not want to set the strips
		from the original shape, use the strips argument.
		"""
		# copy the shape (first to NiTriBasedGeom and then to NiTriStrips)
		strips_ = NifFormat.classes.NiTriStrips().deepcopy(
			NifFormat.classes.NiTriBasedGeom().deepcopy(self))
		# copy the geometry without triangles
		stripsdata = NifFormat.classes.NiTriStripsData().deepcopy(
			NifFormat.classes.NiTriBasedGeomData().deepcopy(self.data))
		# update the shape data
		if strips is None:
			stripsdata.set_strips(self.data.get_strips())
		else:
			stripsdata.set_strips(strips)
		# relink the shape data
		strips_.data = stripsdata
		# and return the result
		return strips_

