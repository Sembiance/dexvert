from itertools import repeat, chain

from nifgen.array import Array
import nifgen.formats.nif as NifFormat
from nifgen.utils.inertia import get_mass_center_inertia_polyhedron
from nifgen.utils.mathutils import float_to_int
from nifgen.array import Array
from nifgen.formats.nif.bshavok.niobjects.BhkShapeCollection import BhkShapeCollection
from nifgen.formats.nif.imports import name_type_map


class BhkPackedNiTriStripsShape(BhkShapeCollection):

	"""
	Bethesda custom hkpShapeCollection using custom packed tri strips data.
	"""

	__name__ = 'bhkPackedNiTriStripsShape'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.num_sub_shapes = name_type_map['Ushort'](self.context, 0, None)
		self.sub_shapes = Array(self.context, 0, None, (0,), name_type_map['HkSubPartData'])
		self.user_data = name_type_map['Uint'].from_value(0)
		self.unused_01 = Array(self.context, 0, None, (0,), name_type_map['Byte'])
		self.radius = name_type_map['Float'].from_value(0.1)
		self.unused_02 = Array(self.context, 0, None, (0,), name_type_map['Byte'])
		self.scale = name_type_map['Vector4'].from_value((1.0, 1.0, 1.0, 0.0))

		# Same as radius
		self.radius_copy = name_type_map['Float'].from_value(0.1)

		# Same as scale.
		self.scale_copy = name_type_map['Vector4'].from_value((1.0, 1.0, 1.0, 0.0))
		self.data = name_type_map['Ref'](self.context, 0, name_type_map['HkPackedNiTriStripsData'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'num_sub_shapes', name_type_map['Ushort'], (0, None), (False, None), (lambda context: context.version <= 335544325, None)
		yield 'sub_shapes', Array, (0, None, (None,), name_type_map['HkSubPartData']), (False, None), (lambda context: context.version <= 335544325, None)
		yield 'user_data', name_type_map['Uint'], (0, None), (False, 0), (None, None)
		yield 'unused_01', Array, (0, None, (4,), name_type_map['Byte']), (False, None), (None, None)
		yield 'radius', name_type_map['Float'], (0, None), (False, 0.1), (None, None)
		yield 'unused_02', Array, (0, None, (4,), name_type_map['Byte']), (False, None), (None, None)
		yield 'scale', name_type_map['Vector4'], (0, None), (False, (1.0, 1.0, 1.0, 0.0)), (None, None)
		yield 'radius_copy', name_type_map['Float'], (0, None), (False, 0.1), (None, None)
		yield 'scale_copy', name_type_map['Vector4'], (0, None), (False, (1.0, 1.0, 1.0, 0.0)), (None, None)
		yield 'data', name_type_map['Ref'], (0, name_type_map['HkPackedNiTriStripsData']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		if instance.context.version <= 335544325:
			yield 'num_sub_shapes', name_type_map['Ushort'], (0, None), (False, None)
			yield 'sub_shapes', Array, (0, None, (instance.num_sub_shapes,), name_type_map['HkSubPartData']), (False, None)
		yield 'user_data', name_type_map['Uint'], (0, None), (False, 0)
		yield 'unused_01', Array, (0, None, (4,), name_type_map['Byte']), (False, None)
		yield 'radius', name_type_map['Float'], (0, None), (False, 0.1)
		yield 'unused_02', Array, (0, None, (4,), name_type_map['Byte']), (False, None)
		yield 'scale', name_type_map['Vector4'], (0, None), (False, (1.0, 1.0, 1.0, 0.0))
		yield 'radius_copy', name_type_map['Float'], (0, None), (False, 0.1)
		yield 'scale_copy', name_type_map['Vector4'], (0, None), (False, (1.0, 1.0, 1.0, 0.0))
		yield 'data', name_type_map['Ref'], (0, name_type_map['HkPackedNiTriStripsData']), (False, None)

	def get_mass_center_inertia(self, density = 1, solid = True):
		"""Return mass, center, and inertia tensor."""
		return get_mass_center_inertia_polyhedron(
			[ vert.as_tuple() for vert in self.data.vertices ],
			[ ( hktriangle.triangle.v_1,
				hktriangle.triangle.v_2,
				hktriangle.triangle.v_3 )
			  for hktriangle in self.data.triangles ],
			density = density, solid = solid)

	def get_sub_shapes(self):
		"""Return sub shapes (works for both Oblivion and Fallout 3)."""
		if self.data and self.data.sub_shapes:
			return self.data.sub_shapes
		else:
			return self.sub_shapes

	def add_shape(self, triangles, normals, vertices, layer=0, material=0):
		"""Pack the given geometry."""
		# add the shape data
		if not self.data:
			self.data = NifFormat.classes.HkPackedNiTriStripsData(self.context)
		data = self.data
		# increase number of shapes
		num_shapes = self.num_sub_shapes
		self.num_sub_shapes = num_shapes + 1
		self.sub_shapes.append(name_type_map['HkSubPartData'](self.context))
		data.num_sub_shapes = num_shapes + 1
		data.sub_shapes.append(name_type_map['HkSubPartData'](self.context))
		# add the shape
		self.sub_shapes[num_shapes].layer = layer
		self.sub_shapes[num_shapes].num_vertices = len(vertices)
		self.sub_shapes[num_shapes].material.material = material
		data.sub_shapes[num_shapes].layer = layer
		data.sub_shapes[num_shapes].num_vertices = len(vertices)
		data.sub_shapes[num_shapes].material.material = material
		firsttriangle = data.num_triangles
		firstvertex = data.num_vertices
		data.num_triangles += len(triangles)
		data.triangles.extend(Array(data.triangles.context, data.triangles.arg, data.triangles.template, len(triangles), data.triangles.dtype))
		for tdata, t, n in zip(data.triangles[firsttriangle:], triangles, normals):
			tdata.triangle.v_1 = t[0] + firstvertex
			tdata.triangle.v_2 = t[1] + firstvertex
			tdata.triangle.v_3 = t[2] + firstvertex
			tdata.normal.x = n[0]
			tdata.normal.y = n[1]
			tdata.normal.z = n[2]
		data.num_vertices += len(vertices)
		data.vertices.extend(Array(data.vertices.context, shape=len(vertices), dtype=data.vertices.dtype))
		for vdata, v in zip(data.vertices[firstvertex:], vertices):
			vdata.x = v[0] / self.context.havok_scale
			vdata.y = v[1] / self.context.havok_scale
			vdata.z = v[2] / self.context.havok_scale
			
	def get_vertex_hash_generator(
		self,
		vertexprecision=3, subshape_index=None):
		"""Generator which produces a tuple of integers for each
		vertex to ease detection of duplicate/close enough to remove
		vertices. The precision parameter denote number of
		significant digits behind the comma.

		For vertexprecision, 3 seems usually enough (maybe we'll
		have to increase this at some point).

		>>> shape = NifFormat.bhkPackedNiTriStripsShape()
		>>> data = NifFormat.hkPackedNiTriStripsData()
		>>> shape.data = data
		>>> shape.num_sub_shapes = 2
		>>> shape.sub_shapes.update_size()
		>>> data.num_vertices = 3
		>>> shape.sub_shapes[0].num_vertices = 2
		>>> shape.sub_shapes[1].num_vertices = 1
		>>> data.vertices.update_size()
		>>> data.vertices[0].x = 0.0
		>>> data.vertices[0].y = 0.1
		>>> data.vertices[0].z = 0.2
		>>> data.vertices[1].x = 1.0
		>>> data.vertices[1].y = 1.1
		>>> data.vertices[1].z = 1.2
		>>> data.vertices[2].x = 2.0
		>>> data.vertices[2].y = 2.1
		>>> data.vertices[2].z = 2.2
		>>> list(shape.get_vertex_hash_generator())
		[(0, (0, 100, 200)), (0, (1000, 1100, 1200)), (1, (2000, 2100, 2200))]
		>>> list(shape.get_vertex_hash_generator(subshape_index=0))
		[(0, 100, 200), (1000, 1100, 1200)]
		>>> list(shape.get_vertex_hash_generator(subshape_index=1))
		[(2000, 2100, 2200)]

		:param vertexprecision: Precision to be used for vertices.
		:type vertexprecision: float
		:return: A generator yielding a hash value for each vertex.
		"""
		vertexfactor = 10 ** vertexprecision
		if subshape_index is None:
			for matid, vert in zip(chain(*[repeat(i, sub_shape.num_vertices)
											for i, sub_shape
											in enumerate(self.get_sub_shapes())]),
									self.data.vertices):
				yield (matid, tuple(float_to_int(value * vertexfactor)
									for value in vert.as_list()))
		else:
			first_vertex = 0
			for i, subshape in zip(range(subshape_index),
								   self.get_sub_shapes()):
				first_vertex += subshape.num_vertices
			for vert_index in range(
				first_vertex,
				first_vertex
				+ self.get_sub_shapes()[subshape_index].num_vertices):
				yield tuple(float_to_int(value * vertexfactor)
							for value
							in self.data.vertices[vert_index].as_list())

	def get_triangle_hash_generator(self):
		"""Generator which produces a tuple of integers, or None
		in degenerate case, for each triangle to ease detection of
		duplicate triangles.

		>>> shape = NifFormat.bhkPackedNiTriStripsShape()
		>>> data = NifFormat.hkPackedNiTriStripsData()
		>>> shape.data = data
		>>> data.num_triangles = 6
		>>> data.triangles.update_size()
		>>> data.triangles[0].triangle.v_1 = 0
		>>> data.triangles[0].triangle.v_2 = 1
		>>> data.triangles[0].triangle.v_3 = 2
		>>> data.triangles[1].triangle.v_1 = 2
		>>> data.triangles[1].triangle.v_2 = 1
		>>> data.triangles[1].triangle.v_3 = 3
		>>> data.triangles[2].triangle.v_1 = 3
		>>> data.triangles[2].triangle.v_2 = 2
		>>> data.triangles[2].triangle.v_3 = 1
		>>> data.triangles[3].triangle.v_1 = 3
		>>> data.triangles[3].triangle.v_2 = 1
		>>> data.triangles[3].triangle.v_3 = 2
		>>> data.triangles[4].triangle.v_1 = 0
		>>> data.triangles[4].triangle.v_2 = 0
		>>> data.triangles[4].triangle.v_3 = 3
		>>> data.triangles[5].triangle.v_1 = 1
		>>> data.triangles[5].triangle.v_2 = 3
		>>> data.triangles[5].triangle.v_3 = 4
		>>> list(shape.get_triangle_hash_generator())
		[(0, 1, 2), (1, 3, 2), (1, 3, 2), (1, 2, 3), None, (1, 3, 4)]

		:return: A generator yielding a hash value for each triangle.
		"""
		for tri in self.data.triangles:
			v_1, v_2, v_3 = tri.triangle.v_1, tri.triangle.v_2, tri.triangle.v_3
			if v_1 == v_2 or v_2 == v_3 or v_3 == v_1:
				# degenerate
				yield None
			elif v_1 < v_2 and v_1 < v_3:
				# v_1 smallest
				yield v_1, v_2, v_3
			elif v_2 < v_1 and v_2 < v_3:
				# v_2 smallest
				yield v_2, v_3, v_1
			else:
				# v_3 smallest
				yield v_3, v_1, v_2

