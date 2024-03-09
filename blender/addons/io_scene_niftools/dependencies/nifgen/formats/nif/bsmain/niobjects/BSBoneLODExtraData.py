from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiExtraData import NiExtraData


class BSBoneLODExtraData(NiExtraData):

	"""
	Unknown
	"""

	__name__ = 'BSBoneLODExtraData'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# Number of bone entries
		self.bone_l_o_d_count = name_type_map['Uint'].from_value(3)

		# Bone Entry
		self.bone_l_o_d_info = Array(self.context, 0, None, (0,), name_type_map['BoneLOD'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'bone_l_o_d_count', name_type_map['Uint'], (0, None), (False, 3), (None, None)
		yield 'bone_l_o_d_info', Array, (0, None, (None,), name_type_map['BoneLOD']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'bone_l_o_d_count', name_type_map['Uint'], (0, None), (False, 3)
		yield 'bone_l_o_d_info', Array, (0, None, (instance.bone_l_o_d_count,), name_type_map['BoneLOD']), (False, None)
