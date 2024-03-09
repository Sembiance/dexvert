from nifgen.array import Array
from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct
from nifgen.formats.wsm.imports import name_type_map


class WsmHeader(MemStruct):

	"""
	56 bytes for JWE2
	"""

	__name__ = 'WsmHeader'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.duration = name_type_map['Float'](self.context, 0, None)

		# likely
		self.frame_count = name_type_map['Uint'](self.context, 0, None)

		# unk
		self.unknowns = Array(self.context, 0, None, (0,), name_type_map['Float'])
		self.locs = name_type_map['ArrayPointer'](self.context, self.frame_count, name_type_map['Vector3'])
		self.quats = name_type_map['ArrayPointer'](self.context, self.frame_count, name_type_map['Vector4'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'duration', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'frame_count', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'unknowns', Array, (0, None, (8,), name_type_map['Float']), (False, None), (None, None)
		yield 'locs', name_type_map['ArrayPointer'], (None, name_type_map['Vector3']), (False, None), (None, None)
		yield 'quats', name_type_map['ArrayPointer'], (None, name_type_map['Vector4']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'duration', name_type_map['Float'], (0, None), (False, None)
		yield 'frame_count', name_type_map['Uint'], (0, None), (False, None)
		yield 'unknowns', Array, (0, None, (8,), name_type_map['Float']), (False, None)
		yield 'locs', name_type_map['ArrayPointer'], (instance.frame_count, name_type_map['Vector3']), (False, None)
		yield 'quats', name_type_map['ArrayPointer'], (instance.frame_count, name_type_map['Vector4']), (False, None)
