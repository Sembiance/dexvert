from nifgen.array import Array
from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class BSGeometrySegmentData(BaseStruct):

	"""
	Bethesda-specific. Describes groups of triangles either segmented in a grid (for LOD) or by body part for skinned FO4 meshes.
	"""

	__name__ = 'BSGeometrySegmentData'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.flags = name_type_map['Byte'](self.context, 0, None)

		# Index = previous Index + previous Num Tris in Segment * 3
		self.start_index = name_type_map['Uint'](self.context, 0, None)

		# The number of triangles belonging to this segment
		self.num_primitives = name_type_map['Uint'](self.context, 0, None)
		self.parent_array_index = name_type_map['Uint'](self.context, 0, None)
		self.num_sub_segments = name_type_map['Uint'](self.context, 0, None)
		self.sub_segment = Array(self.context, 0, None, (0,), name_type_map['BSGeometrySubSegment'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'flags', name_type_map['Byte'], (0, None), (False, None), (lambda context: context.bs_header.bs_version < 130, None)
		yield 'start_index', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'num_primitives', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'parent_array_index', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.bs_header.bs_version >= 130, None)
		yield 'num_sub_segments', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.bs_header.bs_version >= 130, None)
		yield 'sub_segment', Array, (0, None, (None,), name_type_map['BSGeometrySubSegment']), (False, None), (lambda context: context.bs_header.bs_version >= 130, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		if instance.context.bs_header.bs_version < 130:
			yield 'flags', name_type_map['Byte'], (0, None), (False, None)
		yield 'start_index', name_type_map['Uint'], (0, None), (False, None)
		yield 'num_primitives', name_type_map['Uint'], (0, None), (False, None)
		if instance.context.bs_header.bs_version >= 130:
			yield 'parent_array_index', name_type_map['Uint'], (0, None), (False, None)
			yield 'num_sub_segments', name_type_map['Uint'], (0, None), (False, None)
			yield 'sub_segment', Array, (0, None, (instance.num_sub_segments,), name_type_map['BSGeometrySubSegment']), (False, None)
