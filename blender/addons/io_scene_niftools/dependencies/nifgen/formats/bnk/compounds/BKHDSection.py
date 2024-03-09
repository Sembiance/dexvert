from nifgen.array import Array
from nifgen.base_struct import BaseStruct
from nifgen.formats.bnk.imports import name_type_map


class BKHDSection(BaseStruct):

	"""
	First Section of a soundbank aux
	"""

	__name__ = 'BKHDSection'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# length of following data
		self.length = name_type_map['Uint'](self.context, 0, None)
		self.version = name_type_map['Uint'](self.context, 0, None)
		self.id_a = name_type_map['Uint'](self.context, 0, None)
		self.id_b = name_type_map['Uint'](self.context, 0, None)
		self.constant_a = name_type_map['Uint'](self.context, 0, None)
		self.constant_b = name_type_map['Uint'](self.context, 0, None)
		self.unk = name_type_map['Uint'](self.context, 0, None)

		# sometimes present
		self.zeroes = Array(self.context, 0, None, (0,), name_type_map['Ubyte'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'length', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'version', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'id_a', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'id_b', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'constant_a', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'constant_b', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'unk', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'zeroes', Array, (0, None, (None,), name_type_map['Ubyte']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'length', name_type_map['Uint'], (0, None), (False, None)
		yield 'version', name_type_map['Uint'], (0, None), (False, None)
		yield 'id_a', name_type_map['Uint'], (0, None), (False, None)
		yield 'id_b', name_type_map['Uint'], (0, None), (False, None)
		yield 'constant_a', name_type_map['Uint'], (0, None), (False, None)
		yield 'constant_b', name_type_map['Uint'], (0, None), (False, None)
		yield 'unk', name_type_map['Uint'], (0, None), (False, None)
		yield 'zeroes', Array, (0, None, (instance.length - 24,), name_type_map['Ubyte']), (False, None)
