from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class Color4(BaseStruct):

	"""
	A color with alpha (red, green, blue, alpha).
	"""

	__name__ = 'Color4'


	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'r', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'g', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'b', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'a', name_type_map['Float'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'r', name_type_map['Float'], (0, None), (False, None)
		yield 'g', name_type_map['Float'], (0, None), (False, None)
		yield 'b', name_type_map['Float'], (0, None), (False, None)
		yield 'a', name_type_map['Float'], (0, None), (False, None)

	def __init__(self, context=None, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.r = 0
		self.g = 0
		self.b = 0
		self.a = 0

	@classmethod
	def from_value(cls, in_it):
		instance = cls()
		instance.r = in_it[0]
		instance.g = in_it[1]
		instance.b = in_it[2]
		instance.a = in_it[3]
		return instance

	@staticmethod
	def validate_instance(instance, context=None, arg=0, template=None):
		name_type_map["Float"].validate_instance(instance.r)
		name_type_map["Float"].validate_instance(instance.g)
		name_type_map["Float"].validate_instance(instance.b)
		name_type_map["Float"].validate_instance(instance.a)

