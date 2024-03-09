from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiProperty import NiProperty


class NiRimLightProperty(NiProperty):

	__name__ = 'NiRimLightProperty'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# 01 in the example nifs
		self.unknown_byte = name_type_map['Byte'](self.context, 0, None)
		self.unknown_floats = Array(self.context, 0, None, (0,), name_type_map['Float'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'unknown_byte', name_type_map['Byte'], (0, None), (False, None), (None, None)
		yield 'unknown_floats', Array, (0, None, (6,), name_type_map['Float']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'unknown_byte', name_type_map['Byte'], (0, None), (False, None)
		yield 'unknown_floats', Array, (0, None, (6,), name_type_map['Float']), (False, None)
