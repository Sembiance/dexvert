from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiObject import NiObject


class Ni3DsAlphaAnimator(NiObject):

	"""
	Unknown.
	"""

	__name__ = 'Ni3dsAlphaAnimator'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.unknown_1 = Array(self.context, 0, None, (0,), name_type_map['Byte'])
		self.parent = name_type_map['Ref'](self.context, 0, name_type_map['NiObject'])
		self.num_1 = name_type_map['Uint'](self.context, 0, None)
		self.num_2 = name_type_map['Uint'](self.context, 0, None)
		self.unknown_2 = Array(self.context, 0, None, (0,), name_type_map['Uint'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'unknown_1', Array, (0, None, (40,), name_type_map['Byte']), (False, None), (None, None)
		yield 'parent', name_type_map['Ref'], (0, name_type_map['NiObject']), (False, None), (None, None)
		yield 'num_1', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'num_2', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'unknown_2', Array, (0, None, (None, 2,), name_type_map['Uint']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'unknown_1', Array, (0, None, (40,), name_type_map['Byte']), (False, None)
		yield 'parent', name_type_map['Ref'], (0, name_type_map['NiObject']), (False, None)
		yield 'num_1', name_type_map['Uint'], (0, None), (False, None)
		yield 'num_2', name_type_map['Uint'], (0, None), (False, None)
		yield 'unknown_2', Array, (0, None, (instance.num_1 * instance.num_2, 2,), name_type_map['Uint']), (False, None)
