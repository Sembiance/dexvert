from nifgen.base_struct import BaseStruct
from nifgen.formats.ms2.imports import name_type_map


class IKEntry(BaseStruct):

	"""
	60 bytes
	"""

	__name__ = 'IKEntry'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.child = name_type_map['BonePointer'](self.context, 0, None)
		self.parent = name_type_map['BonePointer'](self.context, 0, None)
		self.unk_0 = name_type_map['Ushort'].from_value(0)

		# no clue what space this is in, defines the orientation for the ranges
		self.matrix = name_type_map['Matrix33'](self.context, 0, None)
		self.yaw = name_type_map['RotationRange'](self.context, 0, None)
		self.pitch = name_type_map['RotationRange'](self.context, 0, None)
		self.unk_1 = name_type_map['Uint'].from_value(1)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'child', name_type_map['BonePointer'], (0, None), (False, None), (None, None)
		yield 'parent', name_type_map['BonePointer'], (0, None), (False, None), (None, None)
		yield 'unk_0', name_type_map['Ushort'], (0, None), (False, 0), (None, None)
		yield 'matrix', name_type_map['Matrix33'], (0, None), (False, None), (None, None)
		yield 'yaw', name_type_map['RotationRange'], (0, None), (False, None), (None, None)
		yield 'pitch', name_type_map['RotationRange'], (0, None), (False, None), (None, None)
		yield 'unk_1', name_type_map['Uint'], (0, None), (False, 1), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'child', name_type_map['BonePointer'], (0, None), (False, None)
		yield 'parent', name_type_map['BonePointer'], (0, None), (False, None)
		yield 'unk_0', name_type_map['Ushort'], (0, None), (False, 0)
		yield 'matrix', name_type_map['Matrix33'], (0, None), (False, None)
		yield 'yaw', name_type_map['RotationRange'], (0, None), (False, None)
		yield 'pitch', name_type_map['RotationRange'], (0, None), (False, None)
		yield 'unk_1', name_type_map['Uint'], (0, None), (False, 1)
