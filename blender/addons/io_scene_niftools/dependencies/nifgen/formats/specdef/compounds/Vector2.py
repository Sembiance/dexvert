from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct
from nifgen.formats.specdef.imports import name_type_map


class Vector2(MemStruct):

	"""
	16 bytes
	"""

	__name__ = 'Vector2'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.x = name_type_map['Float'](self.context, 0, None)
		self.y = name_type_map['Float'](self.context, 0, None)
		self.ioptional = name_type_map['Uint'](self.context, 0, None)
		self.unused = name_type_map['Uint'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'x', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'y', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'ioptional', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'unused', name_type_map['Uint'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'x', name_type_map['Float'], (0, None), (False, None)
		yield 'y', name_type_map['Float'], (0, None), (False, None)
		yield 'ioptional', name_type_map['Uint'], (0, None), (False, None)
		yield 'unused', name_type_map['Uint'], (0, None), (False, None)
