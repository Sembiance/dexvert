from nifgen.formats.motiongraph.imports import name_type_map
from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct


class VariableBlendedAnimationData(MemStruct):

	"""
	? bytes
	"""

	__name__ = 'VariableBlendedAnimationData'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.value = name_type_map['Float'].from_value(0.0)
		self._pad = name_type_map['Uint'](self.context, 0, None)
		self.additional_data_streams = name_type_map['DataStreamResourceDataList'](self.context, 0, None)
		self.animation = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'animation', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'value', name_type_map['Float'], (0, None), (False, 0.0), (None, None)
		yield '_pad', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'additional_data_streams', name_type_map['DataStreamResourceDataList'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'animation', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'value', name_type_map['Float'], (0, None), (False, 0.0)
		yield '_pad', name_type_map['Uint'], (0, None), (False, None)
		yield 'additional_data_streams', name_type_map['DataStreamResourceDataList'], (0, None), (False, None)
