from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct
from nifgen.formats.renderparameters.imports import name_type_map


class RenderParameterCurvesRoot(MemStruct):

	"""
	32 bytes
	"""

	__name__ = 'RenderParameterCurvesRoot'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.count = name_type_map['Uint64'](self.context, 0, None)
		self.unk = name_type_map['Uint64'](self.context, 0, None)
		self.param_name = name_type_map['Pointer'](self.context, 0, name_type_map['ZStringObfuscated'])
		self.params = name_type_map['Pointer'](self.context, self.count, name_type_map['CurveParamList'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'param_name', name_type_map['Pointer'], (0, name_type_map['ZStringObfuscated']), (False, None), (None, None)
		yield 'params', name_type_map['Pointer'], (None, name_type_map['CurveParamList']), (False, None), (None, None)
		yield 'count', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'unk', name_type_map['Uint64'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'param_name', name_type_map['Pointer'], (0, name_type_map['ZStringObfuscated']), (False, None)
		yield 'params', name_type_map['Pointer'], (instance.count, name_type_map['CurveParamList']), (False, None)
		yield 'count', name_type_map['Uint64'], (0, None), (False, None)
		yield 'unk', name_type_map['Uint64'], (0, None), (False, None)
