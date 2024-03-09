from nifgen.array import Array
from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct
from nifgen.formats.spl.imports import name_type_map


class SplData(MemStruct):

	"""
	JWE2: 16 + n*16 bytes
	"""

	__name__ = 'SplData'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.offset = name_type_map['Vector3'](self.context, 0, None)
		self.scale = name_type_map['Float'](self.context, 0, None)
		self.keys = Array(self.context, 0, None, (0,), name_type_map['Key'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'offset', name_type_map['Vector3'], (0, None), (False, None), (None, None)
		yield 'scale', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'keys', Array, (0, None, (None,), name_type_map['Key']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'offset', name_type_map['Vector3'], (0, None), (False, None)
		yield 'scale', name_type_map['Float'], (0, None), (False, None)
		yield 'keys', Array, (0, None, (instance.arg,), name_type_map['Key']), (False, None)
