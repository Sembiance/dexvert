from nifgen.array import Array
from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct
from nifgen.formats.tex.imports import name_type_map


class SizeInfo(MemStruct):

	__name__ = 'SizeInfo'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.data = name_type_map['SizeInfoRaw'](self.context, 0, None)
		self.padding = Array(self.context, 0, None, (0,), name_type_map['Ubyte'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'data', name_type_map['SizeInfoRaw'], (0, None), (False, None), (None, None)
		yield 'padding', Array, (0, None, (None,), name_type_map['Ubyte']), (False, None), (lambda context: ((not context.user_version.use_djb) and (context.version == 20)) or (((not context.user_version.use_djb) and (context.version >= 19)) or (context.user_version.use_djb and (context.version == 20))), None)
		yield 'padding', Array, (0, None, (None,), name_type_map['Ubyte']), (False, None), (lambda context: context.user_version.use_djb and (context.version == 19), None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'data', name_type_map['SizeInfoRaw'], (0, None), (False, None)
		if ((not instance.context.user_version.use_djb) and (instance.context.version == 20)) or (((not instance.context.user_version.use_djb) and (instance.context.version >= 19)) or (instance.context.user_version.use_djb and (instance.context.version == 20))):
			yield 'padding', Array, (0, None, (320 - instance.data.io_size,), name_type_map['Ubyte']), (False, None)
		if instance.context.user_version.use_djb and (instance.context.version == 19):
			yield 'padding', Array, (0, None, (384 - instance.data.io_size,), name_type_map['Ubyte']), (False, None)
