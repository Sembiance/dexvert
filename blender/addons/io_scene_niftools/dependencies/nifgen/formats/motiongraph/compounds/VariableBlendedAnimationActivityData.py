from nifgen.formats.motiongraph.imports import name_type_map
from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct


class VariableBlendedAnimationActivityData(MemStruct):

	"""
	? bytes
	"""

	__name__ = 'VariableBlendedAnimationActivityData'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.priorities = name_type_map['Uint'](self.context, 0, None)
		self._pad = name_type_map['Uint'](self.context, 0, None)
		self.weight = name_type_map['FloatInputData'](self.context, 0, None)
		self.animation_count = name_type_map['Uint64'](self.context, 0, None)
		self.variable_blended_animation_flags = name_type_map['Uint'](self.context, 0, None)
		self.animations = name_type_map['ArrayPointer'](self.context, self.animation_count, name_type_map['VariableBlendedAnimationData'])
		self.variable = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'priorities', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield '_pad', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'weight', name_type_map['FloatInputData'], (0, None), (False, None), (None, None)
		yield 'animations', name_type_map['ArrayPointer'], (None, name_type_map['VariableBlendedAnimationData']), (False, None), (None, None)
		yield 'animation_count', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'variable', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'variable_blended_animation_flags', name_type_map['Uint'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'priorities', name_type_map['Uint'], (0, None), (False, None)
		yield '_pad', name_type_map['Uint'], (0, None), (False, None)
		yield 'weight', name_type_map['FloatInputData'], (0, None), (False, None)
		yield 'animations', name_type_map['ArrayPointer'], (instance.animation_count, name_type_map['VariableBlendedAnimationData']), (False, None)
		yield 'animation_count', name_type_map['Uint64'], (0, None), (False, None)
		yield 'variable', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'variable_blended_animation_flags', name_type_map['Uint'], (0, None), (False, None)
