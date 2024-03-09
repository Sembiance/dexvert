from nifgen.base_struct import BaseStruct
from nifgen.formats.ovl.imports import name_type_map


class Triplet(BaseStruct):

	"""
	3 bytes - constant per mime and version
	"""

	__name__ = 'Triplet'

	allow_np = True

	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# ?
		self.a = name_type_map['Ubyte'](self.context, 0, None)

		# ?
		self.b = name_type_map['Ubyte'](self.context, 0, None)

		# ?
		self.c = name_type_map['Ubyte'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'a', name_type_map['Ubyte'], (0, None), (False, None), (None, None)
		yield 'b', name_type_map['Ubyte'], (0, None), (False, None), (None, None)
		yield 'c', name_type_map['Ubyte'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'a', name_type_map['Ubyte'], (0, None), (False, None)
		yield 'b', name_type_map['Ubyte'], (0, None), (False, None)
		yield 'c', name_type_map['Ubyte'], (0, None), (False, None)

	def __eq__(self, other):
		if isinstance(other, Triplet):
			return self.a == other.a and self.b == other.b and self.c == other.c

