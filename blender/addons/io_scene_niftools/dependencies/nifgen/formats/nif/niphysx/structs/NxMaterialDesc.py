from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class NxMaterialDesc(BaseStruct):

	__name__ = 'NxMaterialDesc'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.dynamic_friction = name_type_map['Float'](self.context, 0, None)
		self.static_friction = name_type_map['Float'](self.context, 0, None)
		self.restitution = name_type_map['Float'](self.context, 0, None)
		self.dynamic_friction_v = name_type_map['Float'](self.context, 0, None)
		self.static_friction_v = name_type_map['Float'](self.context, 0, None)
		self.direction_of_anisotropy = name_type_map['Vector3'].from_value((1.0, 0.0, 0.0))
		self.flags = name_type_map['NxMaterialFlag'](self.context, 0, None)
		self.friction_combine_mode = name_type_map['NxCombineMode'](self.context, 0, None)
		self.restitution_combine_mode = name_type_map['NxCombineMode'](self.context, 0, None)
		self.has_spring = name_type_map['Bool'](self.context, 0, None)
		self.spring = name_type_map['NxSpringDesc'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'dynamic_friction', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'static_friction', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'restitution', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'dynamic_friction_v', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'static_friction_v', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'direction_of_anisotropy', name_type_map['Vector3'], (0, None), (False, (1.0, 0.0, 0.0)), (None, None)
		yield 'flags', name_type_map['NxMaterialFlag'], (0, None), (False, None), (None, None)
		yield 'friction_combine_mode', name_type_map['NxCombineMode'], (0, None), (False, None), (None, None)
		yield 'restitution_combine_mode', name_type_map['NxCombineMode'], (0, None), (False, None), (None, None)
		yield 'has_spring', name_type_map['Bool'], (0, None), (False, None), (lambda context: context.version <= 335676160, None)
		yield 'spring', name_type_map['NxSpringDesc'], (0, None), (False, None), (lambda context: context.version <= 335676160, True)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'dynamic_friction', name_type_map['Float'], (0, None), (False, None)
		yield 'static_friction', name_type_map['Float'], (0, None), (False, None)
		yield 'restitution', name_type_map['Float'], (0, None), (False, None)
		yield 'dynamic_friction_v', name_type_map['Float'], (0, None), (False, None)
		yield 'static_friction_v', name_type_map['Float'], (0, None), (False, None)
		yield 'direction_of_anisotropy', name_type_map['Vector3'], (0, None), (False, (1.0, 0.0, 0.0))
		yield 'flags', name_type_map['NxMaterialFlag'], (0, None), (False, None)
		yield 'friction_combine_mode', name_type_map['NxCombineMode'], (0, None), (False, None)
		yield 'restitution_combine_mode', name_type_map['NxCombineMode'], (0, None), (False, None)
		if instance.context.version <= 335676160:
			yield 'has_spring', name_type_map['Bool'], (0, None), (False, None)
		if instance.context.version <= 335676160 and instance.has_spring:
			yield 'spring', name_type_map['NxSpringDesc'], (0, None), (False, None)
