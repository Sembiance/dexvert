from nifgen.formats.curve.imports import name_type_map
from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct


class Key(MemStruct):

	__name__ = 'Key'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.time = name_type_map['Float'](self.context, 0, None)
		self.value = name_type_map['Float'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'time', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'value', name_type_map['Float'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'time', name_type_map['Float'], (0, None), (False, None)
		yield 'value', name_type_map['Float'], (0, None), (False, None)
