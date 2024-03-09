from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiShadeProperty import NiShadeProperty


class BSShaderProperty(NiShadeProperty):

	"""
	Bethesda-specific property.
	"""

	__name__ = 'BSShaderProperty'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.shader_type = name_type_map['BSShaderType'].SHADER_DEFAULT
		self.shader_flags = name_type_map['BSShaderFlags'].from_value(2181038080)
		self.shader_flags_2 = name_type_map['BSShaderFlags2'].from_value(1)

		# Scales the intensity of the environment/cube map.
		self.environment_map_scale = name_type_map['Float'].from_value(1.0)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'shader_type', name_type_map['BSShaderType'], (0, None), (False, name_type_map['BSShaderType'].SHADER_DEFAULT), (lambda context: context.bs_header.bs_version <= 34, None)
		yield 'shader_flags', name_type_map['BSShaderFlags'], (0, None), (False, 2181038080), (lambda context: context.bs_header.bs_version <= 34, None)
		yield 'shader_flags_2', name_type_map['BSShaderFlags2'], (0, None), (False, 1), (lambda context: context.bs_header.bs_version <= 34, None)
		yield 'environment_map_scale', name_type_map['Float'], (0, None), (False, 1.0), (lambda context: context.bs_header.bs_version <= 34, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		if instance.context.bs_header.bs_version <= 34:
			yield 'shader_type', name_type_map['BSShaderType'], (0, None), (False, name_type_map['BSShaderType'].SHADER_DEFAULT)
			yield 'shader_flags', name_type_map['BSShaderFlags'], (0, None), (False, 2181038080)
			yield 'shader_flags_2', name_type_map['BSShaderFlags2'], (0, None), (False, 1)
			yield 'environment_map_scale', name_type_map['Float'], (0, None), (False, 1.0)
