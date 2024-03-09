from nifgen.array import Array
from nifgen.formats.fct.imports import name_type_map
from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct


class FctRoot(MemStruct):

	"""
	JWE: 104 bytes
	"""

	__name__ = 'FctRoot'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.u_0 = name_type_map['Short'](self.context, 0, None)
		self.u_1 = name_type_map['Short'](self.context, 0, None)
		self.a = name_type_map['Float'](self.context, 0, None)
		self.b = name_type_map['Float'](self.context, 0, None)
		self.c = name_type_map['Float'](self.context, 0, None)
		self.minus_1 = name_type_map['Short'](self.context, 0, None)
		self.z_0 = name_type_map['Short'](self.context, 0, None)
		self.z_1 = name_type_map['Int'](self.context, 0, None)
		self.z_2 = name_type_map['Uint64'](self.context, 0, None)
		self.offset = name_type_map['Uint64'](self.context, 0, None)
		self.fonts = Array(self.context, 0, None, (0,), name_type_map['Font'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'u_0', name_type_map['Short'], (0, None), (False, None), (None, None)
		yield 'u_1', name_type_map['Short'], (0, None), (False, None), (None, None)
		yield 'a', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'b', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'c', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'minus_1', name_type_map['Short'], (0, None), (False, None), (None, None)
		yield 'z_0', name_type_map['Short'], (0, None), (False, None), (None, None)
		yield 'z_1', name_type_map['Int'], (0, None), (False, None), (None, None)
		yield 'z_2', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'offset', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'fonts', Array, (0, None, (4,), name_type_map['Font']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'u_0', name_type_map['Short'], (0, None), (False, None)
		yield 'u_1', name_type_map['Short'], (0, None), (False, None)
		yield 'a', name_type_map['Float'], (0, None), (False, None)
		yield 'b', name_type_map['Float'], (0, None), (False, None)
		yield 'c', name_type_map['Float'], (0, None), (False, None)
		yield 'minus_1', name_type_map['Short'], (0, None), (False, None)
		yield 'z_0', name_type_map['Short'], (0, None), (False, None)
		yield 'z_1', name_type_map['Int'], (0, None), (False, None)
		yield 'z_2', name_type_map['Uint64'], (0, None), (False, None)
		yield 'offset', name_type_map['Uint64'], (0, None), (False, None)
		yield 'fonts', Array, (0, None, (4,), name_type_map['Font']), (False, None)
