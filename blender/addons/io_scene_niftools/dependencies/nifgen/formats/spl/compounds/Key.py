from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct
from nifgen.formats.spl.imports import name_type_map


class Key(MemStruct):

	"""
	JWE2: 16 bytes
	"""

	__name__ = 'Key'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.pos = name_type_map['ShortVector3'](self.context, 0, None)
		self.handle_left = name_type_map['ByteVector3'](self.context, 0, None)
		self.handle_right = name_type_map['ByteVector3'](self.context, 0, None)
		self.handle_scale = name_type_map['Float'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'pos', name_type_map['ShortVector3'], (0, None), (False, None), (None, None)
		yield 'handle_left', name_type_map['ByteVector3'], (0, None), (False, None), (None, None)
		yield 'handle_right', name_type_map['ByteVector3'], (0, None), (False, None), (None, None)
		yield 'handle_scale', name_type_map['Float'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'pos', name_type_map['ShortVector3'], (0, None), (False, None)
		yield 'handle_left', name_type_map['ByteVector3'], (0, None), (False, None)
		yield 'handle_right', name_type_map['ByteVector3'], (0, None), (False, None)
		yield 'handle_scale', name_type_map['Float'], (0, None), (False, None)
