from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class BSStreamHeader(BaseStruct):

	"""
	Information about how the file was exported
	"""

	__name__ = 'BSStreamHeader'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.bs_version = name_type_map['Ulittle32'](self.context, 0, None)
		self.author = name_type_map['ExportString'](self.context, 0, None)
		self.unknown_int = name_type_map['Uint'](self.context, 0, None)
		self.process_script = name_type_map['ExportString'](self.context, 0, None)
		self.export_script = name_type_map['ExportString'](self.context, 0, None)
		self.max_filepath = name_type_map['ExportString'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'bs_version', name_type_map['Ulittle32'], (0, None), (False, None), (None, None)
		yield 'author', name_type_map['ExportString'], (0, None), (False, None), (None, None)
		yield 'unknown_int', name_type_map['Uint'], (0, None), (False, None), (None, True)
		yield 'process_script', name_type_map['ExportString'], (0, None), (False, None), (None, True)
		yield 'export_script', name_type_map['ExportString'], (0, None), (False, None), (None, None)
		yield 'max_filepath', name_type_map['ExportString'], (0, None), (False, None), (None, True)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'bs_version', name_type_map['Ulittle32'], (0, None), (False, None)
		yield 'author', name_type_map['ExportString'], (0, None), (False, None)
		if instance.bs_version > 130:
			yield 'unknown_int', name_type_map['Uint'], (0, None), (False, None)
		if instance.bs_version < 131:
			yield 'process_script', name_type_map['ExportString'], (0, None), (False, None)
		yield 'export_script', name_type_map['ExportString'], (0, None), (False, None)
		if instance.bs_version >= 103:
			yield 'max_filepath', name_type_map['ExportString'], (0, None), (False, None)

	@classmethod
	def from_bs_version(cls, context, bs_version):
		instance = cls(context)
		instance.bs_version = bs_version
		for f_name, f_type, arguments, (optional, default) in cls._get_filtered_attribute_list(instance):
			if f_name == "bs_version":
				continue
			else:
				if default is None:
					field_value = f_type(instance, *arguments)
				else:
					field_value = f_type.from_value(*arguments[2:4], default)
			setattr(instance, f_name, field_value)
		return instance

