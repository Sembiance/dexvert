from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class BoneVertData(BaseStruct):

	"""
	NiSkinData::BoneVertData. A vertex and its weight.
	"""

	__name__ = 'BoneVertData'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# The vertex index, in the mesh.
		self.index = name_type_map['Ushort'](self.context, 0, None)

		# The vertex weight - between 0.0 and 1.0
		self.weight = name_type_map['Float'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'index', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'weight', name_type_map['Float'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'index', name_type_map['Ushort'], (0, None), (False, None)
		yield 'weight', name_type_map['Float'], (0, None), (False, None)
