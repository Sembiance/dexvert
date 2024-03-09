from nifgen.array import Array
from nifgen.base_struct import BaseStruct
from nifgen.formats.ms2.imports import name_type_map


class MeshCollisionBit(BaseStruct):

	__name__ = 'MeshCollisionBit'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# ?
		self.a = Array(self.context, 0, None, (0,), name_type_map['Ushort'])

		# incrementing by 16 from 0, or if around 32769: incrementing by 1, mostly
		self.b = Array(self.context, 0, None, (0,), name_type_map['Ushort'])

		# usually, but not always the first value
		self.min_of_b = name_type_map['Ushort'](self.context, 0, None)

		# ?
		self.c = name_type_map['Ushort'](self.context, 0, None)

		# always 2954754766?
		self.consts = Array(self.context, 0, None, (0,), name_type_map['Uint'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'a', Array, (0, None, (24,), name_type_map['Ushort']), (False, None), (None, None)
		yield 'b', Array, (0, None, (8,), name_type_map['Ushort']), (False, None), (None, None)
		yield 'min_of_b', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'c', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'consts', Array, (0, None, (3,), name_type_map['Uint']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'a', Array, (0, None, (24,), name_type_map['Ushort']), (False, None)
		yield 'b', Array, (0, None, (8,), name_type_map['Ushort']), (False, None)
		yield 'min_of_b', name_type_map['Ushort'], (0, None), (False, None)
		yield 'c', name_type_map['Ushort'], (0, None), (False, None)
		yield 'consts', Array, (0, None, (3,), name_type_map['Uint']), (False, None)
