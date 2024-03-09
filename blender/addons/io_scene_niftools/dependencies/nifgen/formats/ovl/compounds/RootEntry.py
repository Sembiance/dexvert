from nifgen.base_struct import BaseStruct
from nifgen.formats.ovl.imports import name_type_map


class RootEntry(BaseStruct):

	"""
	Main file entry in the ovs, one per FileEntry
	"""

	__name__ = 'RootEntry'

	allow_np = True

	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# id (index or djb2) of the file
		self.file_hash = name_type_map['Uint'](self.context, 0, None)

		# djb2 of extension
		self.ext_hash = name_type_map['Uint'](self.context, 0, None)

		# points to the main struct of this file OR -1 pointer for assets
		self.struct_ptr = name_type_map['HeaderPointer'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'file_hash', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'ext_hash', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.version >= 19, None)
		yield 'struct_ptr', name_type_map['HeaderPointer'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'file_hash', name_type_map['Uint'], (0, None), (False, None)
		if instance.context.version >= 19:
			yield 'ext_hash', name_type_map['Uint'], (0, None), (False, None)
		yield 'struct_ptr', name_type_map['HeaderPointer'], (0, None), (False, None)
