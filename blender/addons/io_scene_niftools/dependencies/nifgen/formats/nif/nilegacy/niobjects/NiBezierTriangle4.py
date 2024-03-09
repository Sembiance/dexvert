from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiObject import NiObject


class NiBezierTriangle4(NiObject):

	"""
	LEGACY (pre-10.1)
	Sub data of NiBezierMesh
	"""

	__name__ = 'NiBezierTriangle4'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.unknown_1 = Array(self.context, 0, None, (0,), name_type_map['Uint'])
		self.unknown_2 = name_type_map['Ushort'](self.context, 0, None)
		self.matrix = name_type_map['Matrix33'](self.context, 0, None)
		self.vector_1 = name_type_map['Vector3'](self.context, 0, None)
		self.vector_2 = name_type_map['Vector3'](self.context, 0, None)
		self.unknown_3 = Array(self.context, 0, None, (0,), name_type_map['Short'])
		self.unknown_4 = name_type_map['Byte'](self.context, 0, None)
		self.unknown_5 = name_type_map['Uint'](self.context, 0, None)
		self.unknown_6 = Array(self.context, 0, None, (0,), name_type_map['Short'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'unknown_1', Array, (0, None, (6,), name_type_map['Uint']), (False, None), (None, None)
		yield 'unknown_2', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'matrix', name_type_map['Matrix33'], (0, None), (False, None), (None, None)
		yield 'vector_1', name_type_map['Vector3'], (0, None), (False, None), (None, None)
		yield 'vector_2', name_type_map['Vector3'], (0, None), (False, None), (None, None)
		yield 'unknown_3', Array, (0, None, (4,), name_type_map['Short']), (False, None), (None, None)
		yield 'unknown_4', name_type_map['Byte'], (0, None), (False, None), (None, None)
		yield 'unknown_5', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'unknown_6', Array, (0, None, (24,), name_type_map['Short']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'unknown_1', Array, (0, None, (6,), name_type_map['Uint']), (False, None)
		yield 'unknown_2', name_type_map['Ushort'], (0, None), (False, None)
		yield 'matrix', name_type_map['Matrix33'], (0, None), (False, None)
		yield 'vector_1', name_type_map['Vector3'], (0, None), (False, None)
		yield 'vector_2', name_type_map['Vector3'], (0, None), (False, None)
		yield 'unknown_3', Array, (0, None, (4,), name_type_map['Short']), (False, None)
		yield 'unknown_4', name_type_map['Byte'], (0, None), (False, None)
		yield 'unknown_5', name_type_map['Uint'], (0, None), (False, None)
		yield 'unknown_6', Array, (0, None, (24,), name_type_map['Short']), (False, None)
