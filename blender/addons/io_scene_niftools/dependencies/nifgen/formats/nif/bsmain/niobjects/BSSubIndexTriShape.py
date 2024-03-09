from nifgen.array import Array
from nifgen.formats.nif.bsmain.niobjects.BSTriShape import BSTriShape
from nifgen.formats.nif.imports import name_type_map


class BSSubIndexTriShape(BSTriShape):

	"""
	Fallout 4 Sub-Index Tri Shape
	"""

	__name__ = 'BSSubIndexTriShape'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.num_primitives = name_type_map['Uint'](self.context, 0, None)
		self.num_segments = name_type_map['Uint'](self.context, 0, None)
		self.total_segments = name_type_map['Uint'](self.context, 0, None)
		self.segment = Array(self.context, 0, None, (0,), name_type_map['BSGeometrySegmentData'])
		self.segment_data = name_type_map['BSGeometrySegmentSharedData'](self.context, 0, None)
		self.num_segments = name_type_map['Uint'](self.context, 0, None)
		self.segment = Array(self.context, 0, None, (0,), name_type_map['BSGeometrySegmentData'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'num_primitives', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.bs_header.bs_version >= 130, True)
		yield 'num_segments', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.bs_header.bs_version >= 130, True)
		yield 'total_segments', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.bs_header.bs_version >= 130, True)
		yield 'segment', Array, (0, None, (None,), name_type_map['BSGeometrySegmentData']), (False, None), (lambda context: context.bs_header.bs_version >= 130, True)
		yield 'segment_data', name_type_map['BSGeometrySegmentSharedData'], (0, None), (False, None), (lambda context: context.bs_header.bs_version >= 130, True)
		yield 'num_segments', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.bs_header.bs_version == 100, None)
		yield 'segment', Array, (0, None, (None,), name_type_map['BSGeometrySegmentData']), (False, None), (lambda context: context.bs_header.bs_version == 100, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		if instance.context.bs_header.bs_version >= 130 and instance.data_size > 0:
			yield 'num_primitives', name_type_map['Uint'], (0, None), (False, None)
			yield 'num_segments', name_type_map['Uint'], (0, None), (False, None)
			yield 'total_segments', name_type_map['Uint'], (0, None), (False, None)
			yield 'segment', Array, (0, None, (instance.num_segments,), name_type_map['BSGeometrySegmentData']), (False, None)
		if instance.context.bs_header.bs_version >= 130 and (instance.num_segments < instance.total_segments) and (instance.data_size > 0):
			yield 'segment_data', name_type_map['BSGeometrySegmentSharedData'], (0, None), (False, None)
		if instance.context.bs_header.bs_version == 100:
			yield 'num_segments', name_type_map['Uint'], (0, None), (False, None)
			yield 'segment', Array, (0, None, (instance.num_segments,), name_type_map['BSGeometrySegmentData']), (False, None)

	def get_triangles(self):
		"""Return triangles"""
		return self.triangles

	def get_vertex_data(self):
		return self.vertex_data

