
import logging

from nifgen.base_struct import BaseStruct
from nifgen.formats.ovl.imports import name_type_map


class BufferEntry(BaseStruct):

	"""
	8 bytes
	"""

	__name__ = 'BufferEntry'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# index of buffer in file; id from sorting of data entries
		self.index = name_type_map['Uint'](self.context, 0, None)

		# in bytes
		self.size = name_type_map['Uint'](self.context, 0, None)

		# id; index is taken from buffer group
		self.file_hash = name_type_map['Uint'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'index', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.version <= 19, None)
		yield 'size', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'file_hash', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.version >= 20, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		if instance.context.version <= 19:
			yield 'index', name_type_map['Uint'], (0, None), (False, None)
		yield 'size', name_type_map['Uint'], (0, None), (False, None)
		if instance.context.version >= 20:
			yield 'file_hash', name_type_map['Uint'], (0, None), (False, None)

	def read_data(self, stream):
		"""Load data from archive stream into self for modification and io"""
		self.data = stream.read(self.size)

	def update_data(self, data):
		"""Set data internal data so it can be written on save and update the size value"""
		self.data = data
		self.size = len(data)

	def __eq__(self, other):
		attr_check = ("index", "size", "file_hash")
		same = True
		for attr in attr_check:
			a = getattr(self, attr)
			b = getattr(other, attr)
			if a != b:
				logging.warning(f"Buffer differs for '{attr}' - {a} vs {b}")
				same = False
		return same

