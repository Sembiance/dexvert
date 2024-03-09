from nifgen.base_struct import BaseStruct
from nifgen.formats.ovl.imports import name_type_map


class HeaderPointer(BaseStruct):

	"""
	Not standalone, used by RootEntry, Fragment and DependencyEntry
	"""

	__name__ = 'HeaderPointer'

	allow_np = True

	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# The index of the MemPool this one relates to; OR, for entries referred to from AssetEntries: -1
		self.pool_index = name_type_map['Int'].from_value(-1)

		# the byte offset relative to the start of the MemPool's data
		self.data_offset = name_type_map['Uint'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'pool_index', name_type_map['Int'], (0, None), (False, -1), (None, None)
		yield 'data_offset', name_type_map['Uint'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'pool_index', name_type_map['Int'], (0, None), (False, -1)
		yield 'data_offset', name_type_map['Uint'], (0, None), (False, None)
