from nifgen.array import Array
from nifgen.base_struct import BaseStruct
from nifgen.formats.cdf.imports import name_type_map


class Header(BaseStruct):

	__name__ = 'Header'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# "FACE"
		self.magic = name_type_map['FixedString'](self.context, 4, None)

		# A4 06 00 00, maybe int
		self.unknown_1 = Array(self.context, 0, None, (0,), name_type_map['Ubyte'])

		# Bethesda Softworks
		self.company = name_type_map['ExportString'](self.context, 0, None)

		# Fallout 3
		self.game = name_type_map['ExportString'](self.context, 0, None)

		# This likely contains substructures, can't be bothered to decode right now.
		self.unknown_2 = Array(self.context, 0, None, (0,), name_type_map['Ubyte'])

		# Potentially number of files, but could be something else.
		self.num_files = name_type_map['Littleuint32'](self.context, 0, None)
		self.files = Array(self.context, 0, None, (0,), name_type_map['FileObject'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'magic', name_type_map['FixedString'], (4, None), (False, None), (None, None)
		yield 'unknown_1', Array, (0, None, (4,), name_type_map['Ubyte']), (False, None), (None, None)
		yield 'company', name_type_map['ExportString'], (0, None), (False, None), (None, None)
		yield 'game', name_type_map['ExportString'], (0, None), (False, None), (None, None)
		yield 'unknown_2', Array, (0, None, (2459,), name_type_map['Ubyte']), (False, None), (None, None)
		yield 'num_files', name_type_map['Littleuint32'], (0, None), (False, None), (None, None)
		yield 'files', Array, (0, None, (None,), name_type_map['FileObject']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'magic', name_type_map['FixedString'], (4, None), (False, None)
		yield 'unknown_1', Array, (0, None, (4,), name_type_map['Ubyte']), (False, None)
		yield 'company', name_type_map['ExportString'], (0, None), (False, None)
		yield 'game', name_type_map['ExportString'], (0, None), (False, None)
		yield 'unknown_2', Array, (0, None, (2459,), name_type_map['Ubyte']), (False, None)
		yield 'num_files', name_type_map['Littleuint32'], (0, None), (False, None)
		yield 'files', Array, (0, None, (instance.num_files,), name_type_map['FileObject']), (False, None)
