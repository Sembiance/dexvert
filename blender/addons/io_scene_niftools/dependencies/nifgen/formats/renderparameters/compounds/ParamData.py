from nifgen.array import Array
from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct
from nifgen.formats.renderparameters.imports import name_type_map


class ParamData(MemStruct):

	"""
	16 bytes
	"""

	__name__ = 'ParamData'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.data = Array(self.context, 0, None, (0,), name_type_map['ZStrPtr'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'data', Array, (0, None, (1,), name_type_map['Bool']), (False, None), (None, True)
		yield 'data', Array, (0, None, (1,), name_type_map['Float']), (False, None), (None, True)
		yield 'data', Array, (0, None, (1,), name_type_map['Int']), (False, None), (None, True)
		yield 'data', Array, (0, None, (1,), name_type_map['Uint']), (False, None), (None, True)
		yield 'data', Array, (0, None, (2,), name_type_map['Float']), (False, None), (None, True)
		yield 'data', Array, (0, None, (3,), name_type_map['Float']), (False, None), (None, True)
		yield 'data', Array, (0, None, (4,), name_type_map['Float']), (False, None), (None, True)
		yield 'data', Array, (0, None, (4,), name_type_map['Ubyte']), (False, None), (None, True)
		yield 'data', Array, (0, None, (4,), name_type_map['Float']), (False, None), (None, True)
		yield 'data', Array, (0, None, (1,), name_type_map['ZStrPtr']), (False, None), (None, True)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		if instance.arg == 0:
			yield 'data', Array, (0, None, (1,), name_type_map['Bool']), (False, None)
		if instance.arg == 1:
			yield 'data', Array, (0, None, (1,), name_type_map['Float']), (False, None)
		if instance.arg == 2:
			yield 'data', Array, (0, None, (1,), name_type_map['Int']), (False, None)
		if instance.arg == 3:
			yield 'data', Array, (0, None, (1,), name_type_map['Uint']), (False, None)
		if instance.arg == 4:
			yield 'data', Array, (0, None, (2,), name_type_map['Float']), (False, None)
		if instance.arg == 5:
			yield 'data', Array, (0, None, (3,), name_type_map['Float']), (False, None)
		if instance.arg == 6:
			yield 'data', Array, (0, None, (4,), name_type_map['Float']), (False, None)
		if instance.arg == 7:
			yield 'data', Array, (0, None, (4,), name_type_map['Ubyte']), (False, None)
		if instance.arg == 8:
			yield 'data', Array, (0, None, (4,), name_type_map['Float']), (False, None)
		if instance.arg == 9:
			yield 'data', Array, (0, None, (1,), name_type_map['ZStrPtr']), (False, None)
