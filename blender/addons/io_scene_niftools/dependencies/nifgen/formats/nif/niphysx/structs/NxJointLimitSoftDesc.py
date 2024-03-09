from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class NxJointLimitSoftDesc(BaseStruct):

	__name__ = 'NxJointLimitSoftDesc'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.value = name_type_map['Float'](self.context, 0, None)
		self.restitution = name_type_map['Float'](self.context, 0, None)
		self.spring = name_type_map['Float'](self.context, 0, None)
		self.damping = name_type_map['Float'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'value', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'restitution', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'spring', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'damping', name_type_map['Float'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'value', name_type_map['Float'], (0, None), (False, None)
		yield 'restitution', name_type_map['Float'], (0, None), (False, None)
		yield 'spring', name_type_map['Float'], (0, None), (False, None)
		yield 'damping', name_type_map['Float'], (0, None), (False, None)
