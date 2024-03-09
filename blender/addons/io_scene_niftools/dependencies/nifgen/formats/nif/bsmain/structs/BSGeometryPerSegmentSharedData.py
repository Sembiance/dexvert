from nifgen.array import Array
from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class BSGeometryPerSegmentSharedData(BaseStruct):

	__name__ = 'BSGeometryPerSegmentSharedData'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# If Bone ID is 0xffffffff, this value refers to the Segment at the listed index. Otherwise this is the "Biped Object", which is like the body part types in Skyrim and earlier.
		self.user_index = name_type_map['Uint'](self.context, 0, None)

		# A hash of the bone name string.
		self.bone_id = name_type_map['Uint'].from_value(4294967295)

		# Maximum of 8.
		self.num_cut_offsets = name_type_map['Uint'](self.context, 0, None)
		self.cut_offsets = Array(self.context, 0, None, (0,), name_type_map['Float'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'user_index', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'bone_id', name_type_map['Uint'], (0, None), (False, 4294967295), (None, None)
		yield 'num_cut_offsets', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'cut_offsets', Array, (0, None, (None,), name_type_map['Float']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'user_index', name_type_map['Uint'], (0, None), (False, None)
		yield 'bone_id', name_type_map['Uint'], (0, None), (False, 4294967295)
		yield 'num_cut_offsets', name_type_map['Uint'], (0, None), (False, None)
		yield 'cut_offsets', Array, (0, None, (instance.num_cut_offsets,), name_type_map['Float']), (False, None)
