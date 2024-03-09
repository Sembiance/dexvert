import os

from nifgen.base_struct import BaseStruct
from nifgen.formats.ovl.imports import name_type_map


class Fragment(BaseStruct):

	"""
	These are to be thought of as instructions for loading. Their order is irrelevant.
	"""

	__name__ = 'Fragment'

	allow_np = True

	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# determines where to write a pointer address
		self.link_ptr = name_type_map['HeaderPointer'](self.context, 0, None)

		# the struct that is pointed to can be found here
		self.struct_ptr = name_type_map['HeaderPointer'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'link_ptr', name_type_map['HeaderPointer'], (0, None), (False, None), (None, None)
		yield 'struct_ptr', name_type_map['HeaderPointer'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'link_ptr', name_type_map['HeaderPointer'], (0, None), (False, None)
		yield 'struct_ptr', name_type_map['HeaderPointer'], (0, None), (False, None)

	@property
	def ext(self):
		return self.ext_raw.replace(":", ".")

	@ext.setter
	def ext(self, e):
		self.ext_raw = e.replace(".", ":")

	def register(self, pools):
		self.struct_ptr.add_struct(pools)
		target_pool = pools[self.struct_ptr.pool_index]
		self.link_ptr.add_link((target_pool, self.struct_ptr.data_offset), pools)

