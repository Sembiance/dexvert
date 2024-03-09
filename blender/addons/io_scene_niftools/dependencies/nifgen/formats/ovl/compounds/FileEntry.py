from nifgen.base_struct import BaseStruct
from nifgen.formats.ovl.imports import name_type_map


class FileEntry(BaseStruct):

	"""
	Description of one file in the archive
	"""

	__name__ = 'FileEntry'

	allow_np = True

	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.basename = name_type_map['OffsetString'](self.context, self.context.names, None)

		# this hash is used to retrieve the file name from inside the archive
		self.file_hash = name_type_map['Uint'](self.context, 0, None)

		# pool type of this file's root pointer, if part of a set, it's usually the same as set pool type
		self.pool_type = name_type_map['Byte'](self.context, 0, None)

		# if this file is part of a set, the set's root entry's pool type, else 0
		self.set_pool_type = name_type_map['Byte'](self.context, 0, None)

		# index into 'Extensions' array
		self.extension = name_type_map['Ushort'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'basename', name_type_map['OffsetString'], (None, None), (False, None), (None, None)
		yield 'file_hash', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'pool_type', name_type_map['Byte'], (0, None), (False, None), (None, None)
		yield 'set_pool_type', name_type_map['Byte'], (0, None), (False, None), (None, None)
		yield 'extension', name_type_map['Ushort'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'basename', name_type_map['OffsetString'], (instance.context.names, None), (False, None)
		yield 'file_hash', name_type_map['Uint'], (0, None), (False, None)
		yield 'pool_type', name_type_map['Byte'], (0, None), (False, None)
		yield 'set_pool_type', name_type_map['Byte'], (0, None), (False, None)
		yield 'extension', name_type_map['Ushort'], (0, None), (False, None)

	def update_constants(self, ovl):
		"""Update the constants"""
		self.pool_type = ovl.get_mime(self.ext, "pool")
		self.set_pool_type = ovl.get_mime(self.ext, "set_pool")

