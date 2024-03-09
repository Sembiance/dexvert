import nifgen.formats.nif as NifFormat
from nifgen.array import Array
from nifgen.formats.nif.bshavok.niobjects.BhkShapeCollection import BhkShapeCollection
from nifgen.formats.nif.imports import name_type_map


class HkPackedNiTriStripsData(BhkShapeCollection):

	"""
	Bethesda custom tri strips data block for bhkPackedNiTriStripsShape.
	"""

	__name__ = 'hkPackedNiTriStripsData'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.num_triangles = name_type_map['Uint'](self.context, 0, None)
		self.triangles = Array(self.context, 0, None, (0,), name_type_map['TriangleData'])
		self.num_vertices = name_type_map['Uint'](self.context, 0, None)
		self.compressed = name_type_map['Bool'](self.context, 0, None)
		self.vertices = Array(self.context, 0, None, (0,), name_type_map['Vector3'])

		# Compression on read may not be supported. Vertices may be packed in ushort that are not IEEE standard half-precision.
		self.compressed_vertices = Array(self.context, 0, None, (0,), name_type_map['HalfVector3'])
		self.num_sub_shapes = name_type_map['Ushort'](self.context, 0, None)
		self.sub_shapes = Array(self.context, 0, None, (0,), name_type_map['HkSubPartData'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'num_triangles', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'triangles', Array, (0, None, (None,), name_type_map['TriangleData']), (False, None), (None, None)
		yield 'num_vertices', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'compressed', name_type_map['Bool'], (0, None), (False, None), (lambda context: context.version >= 335675399, None)
		yield 'vertices', Array, (0, None, (None,), name_type_map['Vector3']), (False, None), (None, True)
		yield 'compressed_vertices', Array, (0, None, (None,), name_type_map['HalfVector3']), (False, None), (None, True)
		yield 'num_sub_shapes', name_type_map['Ushort'], (0, None), (False, None), (lambda context: context.version >= 335675399, None)
		yield 'sub_shapes', Array, (0, None, (None,), name_type_map['HkSubPartData']), (False, None), (lambda context: context.version >= 335675399, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'num_triangles', name_type_map['Uint'], (0, None), (False, None)
		yield 'triangles', Array, (0, None, (instance.num_triangles,), name_type_map['TriangleData']), (False, None)
		yield 'num_vertices', name_type_map['Uint'], (0, None), (False, None)
		if instance.context.version >= 335675399:
			yield 'compressed', name_type_map['Bool'], (0, None), (False, None)
		if instance.compressed == 0:
			yield 'vertices', Array, (0, None, (instance.num_vertices,), name_type_map['Vector3']), (False, None)
		if instance.compressed != 0:
			yield 'compressed_vertices', Array, (0, None, (instance.num_vertices,), name_type_map['HalfVector3']), (False, None)
		if instance.context.version >= 335675399:
			yield 'num_sub_shapes', name_type_map['Ushort'], (0, None), (False, None)
			yield 'sub_shapes', Array, (0, None, (instance.num_sub_shapes,), name_type_map['HkSubPartData']), (False, None)
	def apply_scale(self, scale):
		"""Apply scale factor on data."""
		if abs(scale - 1.0) <= NifFormat.EPSILON:
			return
		super().apply_scale(scale)
		for vert in self.vertices:
			vert.x *= scale
			vert.y *= scale
			vert.z *= scale

