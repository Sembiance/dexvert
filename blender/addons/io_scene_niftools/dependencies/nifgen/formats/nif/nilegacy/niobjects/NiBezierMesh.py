from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiAVObject import NiAVObject


class NiBezierMesh(NiAVObject):

	"""
	LEGACY (pre-10.1)
	Unknown
	"""

	__name__ = 'NiBezierMesh'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.num_bezier_triangles = name_type_map['Uint'](self.context, 0, None)
		self.bezier_triangle = Array(self.context, 0, name_type_map['NiBezierTriangle4'], (0,), name_type_map['Ref'])
		self.unknown_3 = name_type_map['Uint'](self.context, 0, None)
		self.count_1 = name_type_map['Ushort'](self.context, 0, None)
		self.unknown_4 = name_type_map['Ushort'](self.context, 0, None)
		self.points_1 = Array(self.context, 0, None, (0,), name_type_map['Vector3'])
		self.unknown_5 = name_type_map['Uint'](self.context, 0, None)
		self.points_2 = Array(self.context, 0, None, (0,), name_type_map['Float'])
		self.unknown_6 = name_type_map['Uint'](self.context, 0, None)
		self.count_2 = name_type_map['Ushort'](self.context, 0, None)
		self.data_2 = Array(self.context, 0, None, (0,), name_type_map['Ushort'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'num_bezier_triangles', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'bezier_triangle', Array, (0, name_type_map['NiBezierTriangle4'], (None,), name_type_map['Ref']), (False, None), (None, None)
		yield 'unknown_3', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'count_1', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'unknown_4', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'points_1', Array, (0, None, (None,), name_type_map['Vector3']), (False, None), (None, None)
		yield 'unknown_5', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'points_2', Array, (0, None, (None, 2,), name_type_map['Float']), (False, None), (None, None)
		yield 'unknown_6', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'count_2', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'data_2', Array, (0, None, (None, 4,), name_type_map['Ushort']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'num_bezier_triangles', name_type_map['Uint'], (0, None), (False, None)
		yield 'bezier_triangle', Array, (0, name_type_map['NiBezierTriangle4'], (instance.num_bezier_triangles,), name_type_map['Ref']), (False, None)
		yield 'unknown_3', name_type_map['Uint'], (0, None), (False, None)
		yield 'count_1', name_type_map['Ushort'], (0, None), (False, None)
		yield 'unknown_4', name_type_map['Ushort'], (0, None), (False, None)
		yield 'points_1', Array, (0, None, (instance.count_1,), name_type_map['Vector3']), (False, None)
		yield 'unknown_5', name_type_map['Uint'], (0, None), (False, None)
		yield 'points_2', Array, (0, None, (instance.count_1, 2,), name_type_map['Float']), (False, None)
		yield 'unknown_6', name_type_map['Uint'], (0, None), (False, None)
		yield 'count_2', name_type_map['Ushort'], (0, None), (False, None)
		yield 'data_2', Array, (0, None, (instance.count_2, 4,), name_type_map['Ushort']), (False, None)
