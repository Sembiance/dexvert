from nifgen.array import Array
from nifgen.formats.nif.bshavok.niobjects.BhkAction import BhkAction
from nifgen.formats.nif.imports import name_type_map


class BhkLiquidAction(BhkAction):

	"""
	Bethesda custom bhkUnaryAction. Does not hold a link to the body like other bhkUnaryActions however.
	"""

	__name__ = 'bhkLiquidAction'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.unused_01 = Array(self.context, 0, None, (0,), name_type_map['Byte'])
		self.initial_stick_force = name_type_map['Float'].from_value(25.0)
		self.stick_strength = name_type_map['Float'].from_value(100.0)
		self.neighbor_distance = name_type_map['Float'].from_value(128.0)
		self.neighbor_strength = name_type_map['Float'].from_value(500.0)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'unused_01', Array, (0, None, (12,), name_type_map['Byte']), (False, None), (None, None)
		yield 'initial_stick_force', name_type_map['Float'], (0, None), (False, 25.0), (None, None)
		yield 'stick_strength', name_type_map['Float'], (0, None), (False, 100.0), (None, None)
		yield 'neighbor_distance', name_type_map['Float'], (0, None), (False, 128.0), (None, None)
		yield 'neighbor_strength', name_type_map['Float'], (0, None), (False, 500.0), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'unused_01', Array, (0, None, (12,), name_type_map['Byte']), (False, None)
		yield 'initial_stick_force', name_type_map['Float'], (0, None), (False, 25.0)
		yield 'stick_strength', name_type_map['Float'], (0, None), (False, 100.0)
		yield 'neighbor_distance', name_type_map['Float'], (0, None), (False, 128.0)
		yield 'neighbor_strength', name_type_map['Float'], (0, None), (False, 500.0)
