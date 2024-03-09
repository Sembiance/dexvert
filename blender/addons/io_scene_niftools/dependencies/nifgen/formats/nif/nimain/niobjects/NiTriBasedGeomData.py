import nifgen.formats.nif as NifFormat
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiGeometryData import NiGeometryData


class NiTriBasedGeomData(NiGeometryData):

	"""
	Describes a mesh, built from triangles.
	"""

	__name__ = 'NiTriBasedGeomData'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# Number of triangles.
		self.num_triangles = name_type_map['Ushort'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'num_triangles', name_type_map['Ushort'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'num_triangles', name_type_map['Ushort'], (0, None), (False, None)
	def is_interchangeable(self, other):
		"""Heuristically checks if two NiTriBasedGeomData blocks describe
		the same geometry, that is, if they can be used interchangeably in
		a NIF file without affecting the rendering. The check is not fool
		proof but has shown to work in most practical cases.

		:param other: Another geometry data block.
		:type other: L{NifFormat.NiTriBasedGeomData} (if it has another type
			then the function will always return ``False``)
		:return: ``True`` if the geometries are equivalent, ``False`` otherwise.
		"""
		# check for object identity
		if self is other:
			return True

		# type check
		if not isinstance(other, NifFormat.classes.NiTriBasedGeomData):
			return False

		# check class
		if (not isinstance(self, other.__class__)
			or not isinstance(other, self.__class__)):
			return False

		# check some trivial things first
		for attribute in (
			"num_vertices", "keep_flags", "compress_flags", "has_vertices",
			"num_uv_sets", "has_normals", "center", "radius",
			"has_vertex_colors", "has_uv", "consistency_flags"):
			if getattr(self, attribute) != getattr(other, attribute):
				return False

		# check vertices (this includes uvs, vcols and normals)
		verthashes1 = [hsh for hsh in self.get_vertex_hash_generator()]
		verthashes2 = [hsh for hsh in other.get_vertex_hash_generator()]
		for hash1 in verthashes1:
			if not hash1 in verthashes2:
				return False
		for hash2 in verthashes2:
			if not hash2 in verthashes1:
				return False

		# check triangle list
		triangles1 = [tuple(verthashes1[i] for i in tri)
					  for tri in self.get_triangles()]
		triangles2 = [tuple(verthashes2[i] for i in tri)
					  for tri in other.get_triangles()]
		for tri1 in triangles1:
			if not tri1 in triangles2:
				return False
		for tri2 in triangles2:
			if not tri2 in triangles1:
				return False

		# looks pretty identical!
		return True

	def get_triangle_indices(self, triangles):
		"""Yield list of triangle indices (relative to
		self.get_triangles()) of given triangles. Degenerate triangles in
		the list are assigned index ``None``.

		>>> from pyffi.formats.nif import NifFormat
		>>> geomdata = NifFormat.NiTriShapeData()
		>>> geomdata.set_triangles([(0,1,2),(1,2,3),(2,3,4)])
		>>> list(geomdata.get_triangle_indices([(1,2,3)]))
		[1]
		>>> list(geomdata.get_triangle_indices([(3,1,2)]))
		[1]
		>>> list(geomdata.get_triangle_indices([(2,3,1)]))
		[1]
		>>> list(geomdata.get_triangle_indices([(1,2,0),(4,2,3)]))
		[0, 2]
		>>> list(geomdata.get_triangle_indices([(0,0,0),(4,2,3)]))
		[None, 2]
		>>> list(geomdata.get_triangle_indices([(0,3,4),(4,2,3)])) # doctest: +ELLIPSIS
		Traceback (most recent call last):
			...
		ValueError: ...

		:param triangles: An iterable of triangles to check.
		:type triangles: iterator or list of tuples of three ints
		"""
		def triangleHash(triangle):
			"""Calculate hash of a non-degenerate triangle.
			Returns ``None`` if the triangle is degenerate.
			"""
			if triangle[0] < triangle[1] and triangle[0] < triangle[2]:
				return hash((triangle[0], triangle[1], triangle[2]))
			elif triangle[1] < triangle[0] and triangle[1] < triangle[2]:
				return hash((triangle[1], triangle[2], triangle[0]))
			elif triangle[2] < triangle[0] and triangle[2] < triangle[1]:
				return hash((triangle[2], triangle[0], triangle[1]))

		# calculate hashes of all triangles in the geometry
		self_triangles_hashes = [
			triangleHash(triangle) for triangle in self.get_triangles()]

		# calculate index of each triangle in the list of triangles
		for triangle in triangles:
			triangle_hash = triangleHash(triangle)
			if triangle_hash is None:
				yield None
			else:
				yield self_triangles_hashes.index(triangle_hash)

