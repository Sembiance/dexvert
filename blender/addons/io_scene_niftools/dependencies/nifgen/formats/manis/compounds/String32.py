from nifgen.base_struct import BaseStruct
from nifgen.formats.manis.imports import name_type_map


class String32(BaseStruct):

	__name__ = 'String32'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.ref = name_type_map['Empty'](self.context, 0, None)
		self.name = name_type_map['ZString'](self.context, 0, None)
		self.pad = name_type_map['PadAlign'](self.context, 32, self.ref)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'ref', name_type_map['Empty'], (0, None), (False, None), (None, None)
		yield 'name', name_type_map['ZString'], (0, None), (False, None), (None, None)
		yield 'pad', name_type_map['PadAlign'], (32, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'ref', name_type_map['Empty'], (0, None), (False, None)
		yield 'name', name_type_map['ZString'], (0, None), (False, None)
		yield 'pad', name_type_map['PadAlign'], (32, instance.ref), (False, None)
