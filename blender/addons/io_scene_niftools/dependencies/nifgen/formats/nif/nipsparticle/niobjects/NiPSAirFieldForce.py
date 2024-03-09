from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nipsparticle.niobjects.NiPSFieldForce import NiPSFieldForce


class NiPSAirFieldForce(NiPSFieldForce):

	"""
	Inside a field, updates particle velocity to simulate the effects of air movements.
	"""

	__name__ = 'NiPSAirFieldForce'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.direction = name_type_map['Vector3'](self.context, 0, None)
		self.air_friction = name_type_map['Float'](self.context, 0, None)
		self.inherited_velocity = name_type_map['Float'](self.context, 0, None)
		self.inherit_rotation = name_type_map['Bool'](self.context, 0, None)
		self.enable_spread = name_type_map['Bool'](self.context, 0, None)
		self.spread = name_type_map['Float'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'direction', name_type_map['Vector3'], (0, None), (False, None), (None, None)
		yield 'air_friction', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'inherited_velocity', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'inherit_rotation', name_type_map['Bool'], (0, None), (False, None), (None, None)
		yield 'enable_spread', name_type_map['Bool'], (0, None), (False, None), (None, None)
		yield 'spread', name_type_map['Float'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'direction', name_type_map['Vector3'], (0, None), (False, None)
		yield 'air_friction', name_type_map['Float'], (0, None), (False, None)
		yield 'inherited_velocity', name_type_map['Float'], (0, None), (False, None)
		yield 'inherit_rotation', name_type_map['Bool'], (0, None), (False, None)
		yield 'enable_spread', name_type_map['Bool'], (0, None), (False, None)
		yield 'spread', name_type_map['Float'], (0, None), (False, None)
