from nifgen.base_struct import BaseStruct
from nifgen.formats.ms2.imports import name_type_map


class MaterialName(BaseStruct):

	__name__ = 'MaterialName'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# index into ms2 names array
		self.name_index = name_type_map['Uint'](self.context, 0, None)

		# specifies the blend mode, highly consistent to shader type used
		# PZ: 263: {'furshell', 'furpatchworkbaldnessshell', 'furpatchworkshell'}, 6: {'furpatchworkbaldnessfin', 'furfin', 'furpatchworkfin'}, 8: {'animal_whisker'}, 15: {'glass_textured_weather'}
		# JWE2: 7: {'dinosaurfur_vanilla_shell'}, 6: {'dinosaurfur_vanilla_fin'}
		self.blend_mode = name_type_map['Uint'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'name_index', name_type_map['Ushort'], (0, None), (False, None), (lambda context: context.version <= 32, None)
		yield 'name_index', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.version >= 47, None)
		yield 'blend_mode', name_type_map['Ushort'], (0, None), (False, None), (lambda context: context.version <= 32, None)
		yield 'blend_mode', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.version >= 47, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		if instance.context.version <= 32:
			yield 'name_index', name_type_map['Ushort'], (0, None), (False, None)
		if instance.context.version >= 47:
			yield 'name_index', name_type_map['Uint'], (0, None), (False, None)
		if instance.context.version <= 32:
			yield 'blend_mode', name_type_map['Ushort'], (0, None), (False, None)
		if instance.context.version >= 47:
			yield 'blend_mode', name_type_map['Uint'], (0, None), (False, None)
