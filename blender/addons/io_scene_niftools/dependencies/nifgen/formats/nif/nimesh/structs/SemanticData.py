from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class SemanticData(BaseStruct):

	__name__ = 'SemanticData'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# Type of data (POSITION, POSITION_BP, INDEX, NORMAL, NORMAL_BP,
		# TEXCOORD, BLENDINDICES, BLENDWEIGHT, BONE_PALETTE, COLOR, DISPLAYLIST,
		# MORPH_POSITION, BINORMAL_BP, TANGENT, TANGENT_BP).
		self.name = name_type_map['NiFixedString'](self.context, 0, None)

		# An extra index of the data. For example, if there are 3 uv maps,
		# then the corresponding TEXCOORD data components would have indices
		# 0, 1, and 2, respectively.
		self.index = name_type_map['Uint'].from_value(0)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'name', name_type_map['NiFixedString'], (0, None), (False, None), (None, None)
		yield 'index', name_type_map['Uint'], (0, None), (False, 0), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'name', name_type_map['NiFixedString'], (0, None), (False, None)
		yield 'index', name_type_map['Uint'], (0, None), (False, 0)
