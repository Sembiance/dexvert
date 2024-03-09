from nifgen.array import Array
from nifgen.base_struct import BaseStruct
from nifgen.formats.cdf.imports import name_type_map


class FileObject(BaseStruct):

	__name__ = 'FileObject'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.path = name_type_map['SizedString'](self.context, 0, None)
		self.file_size = name_type_map['Littleuint32'](self.context, 0, None)

		# Can be any kind of file, type presumably determined by file extension.
		self.file = Array(self.context, 0, None, (0,), name_type_map['Ubyte'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'path', name_type_map['SizedString'], (0, None), (False, None), (None, None)
		yield 'file_size', name_type_map['Littleuint32'], (0, None), (False, None), (None, None)
		yield 'file', Array, (0, None, (None,), name_type_map['Ubyte']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'path', name_type_map['SizedString'], (0, None), (False, None)
		yield 'file_size', name_type_map['Littleuint32'], (0, None), (False, None)
		yield 'file', Array, (0, None, (instance.file_size,), name_type_map['Ubyte']), (False, None)
