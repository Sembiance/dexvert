import os

from nifgen.base_struct import BaseStruct
from nifgen.formats.ovl.imports import name_type_map


class DependencyEntry(BaseStruct):

	"""
	Description of dependency; links it to an entry from this archive
	"""

	__name__ = 'DependencyEntry'

	allow_np = True

	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# basename for dependency, for lookup in hash dict. Can be either external or internal.
		self.file_hash = name_type_map['Uint'](self.context, 0, None)

		# ext for dependency, use : instead of . at the start, eg. :tex
		self.ext_raw = name_type_map['OffsetString'](self.context, self.context.names, None)

		# index into ovl files, points to the file entry using this dependency
		self.file_index = name_type_map['Uint'](self.context, 0, None)

		# pointer into flattened list of all archives' pools
		self.link_ptr = name_type_map['HeaderPointer'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'file_hash', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'ext_raw', name_type_map['OffsetString'], (None, None), (False, None), (None, None)
		yield 'file_index', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'link_ptr', name_type_map['HeaderPointer'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'file_hash', name_type_map['Uint'], (0, None), (False, None)
		yield 'ext_raw', name_type_map['OffsetString'], (instance.context.names, None), (False, None)
		yield 'file_index', name_type_map['Uint'], (0, None), (False, None)
		yield 'link_ptr', name_type_map['HeaderPointer'], (0, None), (False, None)

	@property
	def ext(self):
		return self.ext_raw.replace(":", ".")

	@ext.setter
	def ext(self, e):
		self.ext_raw = e.replace(".", ":")

	def register(self, pools):
		# name is already set at this point
		self.link_ptr.add_link(self.name, pools)

