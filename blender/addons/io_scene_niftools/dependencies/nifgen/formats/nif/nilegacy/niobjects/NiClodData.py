from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiTriBasedGeomData import NiTriBasedGeomData


class NiClodData(NiTriBasedGeomData):

	"""
	Holds mesh data for continuous level of detail shapes.
	Presumably a progressive mesh with triangles specified by edge splits.
	Found in: Freedom Force, Spellbinder
	"""

	__name__ = 'NiClodData'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.unknown_shorts = name_type_map['Ushort'](self.context, 0, None)
		self.unknown_count_1 = name_type_map['Ushort'](self.context, 0, None)
		self.unknown_count_2 = name_type_map['Ushort'](self.context, 0, None)
		self.unknown_count_3 = name_type_map['Ushort'](self.context, 0, None)
		self.unknown_float = name_type_map['Float'](self.context, 0, None)
		self.unknown_short = name_type_map['Ushort'](self.context, 0, None)
		self.unknown_clod_shorts_1 = Array(self.context, 0, None, (0,), name_type_map['Ushort'])
		self.unknown_clod_shorts_2 = Array(self.context, 0, None, (0,), name_type_map['Ushort'])
		self.unknown_clod_shorts_3 = Array(self.context, 0, None, (0,), name_type_map['Ushort'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'unknown_shorts', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'unknown_count_1', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'unknown_count_2', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'unknown_count_3', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'unknown_float', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'unknown_short', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'unknown_clod_shorts_1', Array, (0, None, (None, 6,), name_type_map['Ushort']), (False, None), (None, None)
		yield 'unknown_clod_shorts_2', Array, (0, None, (None,), name_type_map['Ushort']), (False, None), (None, None)
		yield 'unknown_clod_shorts_3', Array, (0, None, (None, 6,), name_type_map['Ushort']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'unknown_shorts', name_type_map['Ushort'], (0, None), (False, None)
		yield 'unknown_count_1', name_type_map['Ushort'], (0, None), (False, None)
		yield 'unknown_count_2', name_type_map['Ushort'], (0, None), (False, None)
		yield 'unknown_count_3', name_type_map['Ushort'], (0, None), (False, None)
		yield 'unknown_float', name_type_map['Float'], (0, None), (False, None)
		yield 'unknown_short', name_type_map['Ushort'], (0, None), (False, None)
		yield 'unknown_clod_shorts_1', Array, (0, None, (instance.unknown_count_1, 6,), name_type_map['Ushort']), (False, None)
		yield 'unknown_clod_shorts_2', Array, (0, None, (instance.unknown_count_2,), name_type_map['Ushort']), (False, None)
		yield 'unknown_clod_shorts_3', Array, (0, None, (instance.unknown_count_3, 6,), name_type_map['Ushort']), (False, None)
