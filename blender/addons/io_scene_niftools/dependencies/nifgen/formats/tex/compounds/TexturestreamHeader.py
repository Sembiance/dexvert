from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct
from nifgen.formats.tex.imports import name_type_map


class TexturestreamHeader(MemStruct):

	"""
	JWE, PZ, PC: 8 bytes
	JWE2: 16 bytes
	"""

	__name__ = 'TexturestreamHeader'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.zero = name_type_map['Uint64'].from_value(0)
		self.lod_index = name_type_map['Uint64'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'zero', name_type_map['Uint64'], (0, None), (True, 0), (None, None)
		yield 'lod_index', name_type_map['Uint64'], (0, None), (False, None), (lambda context: context.user_version.use_djb and (context.version == 20), None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'zero', name_type_map['Uint64'], (0, None), (True, 0)
		if instance.context.user_version.use_djb and (instance.context.version == 20):
			yield 'lod_index', name_type_map['Uint64'], (0, None), (False, None)
