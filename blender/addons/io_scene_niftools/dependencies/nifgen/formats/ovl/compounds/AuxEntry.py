from nifgen.base_struct import BaseStruct
from nifgen.formats.ovl.imports import name_type_map


class AuxEntry(BaseStruct):

	"""
	describes an external AUX resource
	"""

	__name__ = 'AuxEntry'

	allow_np = True

	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# index into files list
		self.file_index = name_type_map['Uint'](self.context, 0, None)
		self.basename = name_type_map['OffsetString'](self.context, self.context.names, None)

		# byte count of the complete external resource file
		self.size = name_type_map['Uint'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'file_index', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'basename', name_type_map['OffsetString'], (None, None), (False, None), (None, None)
		yield 'size', name_type_map['Uint'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'file_index', name_type_map['Uint'], (0, None), (False, None)
		yield 'basename', name_type_map['OffsetString'], (instance.context.names, None), (False, None)
		yield 'size', name_type_map['Uint'], (0, None), (False, None)
