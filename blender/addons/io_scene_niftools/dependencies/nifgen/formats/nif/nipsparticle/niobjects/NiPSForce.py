from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiObject import NiObject


class NiPSForce(NiObject):

	"""
	Abstract base class for all particle forces.
	"""

	__name__ = 'NiPSForce'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.name = name_type_map['NiFixedString'](self.context, 0, None)

		# The force type is set by each derived class and cannot be changed.
		self.type = name_type_map['PSForceType'](self.context, 0, None)
		self.active = name_type_map['Bool'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'name', name_type_map['NiFixedString'], (0, None), (False, None), (None, None)
		yield 'type', name_type_map['PSForceType'], (0, None), (False, None), (None, None)
		yield 'active', name_type_map['Bool'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'name', name_type_map['NiFixedString'], (0, None), (False, None)
		if isinstance(instance, name_type_map['NiPSGravityForce']):
			yield 'type', name_type_map['PSForceType'], (0, None), (False, name_type_map['PSForceType'].FORCE_GRAVITY)
		elif isinstance(instance, name_type_map['NiPSVortexFieldForce']):
			yield 'type', name_type_map['PSForceType'], (0, None), (False, name_type_map['PSForceType'].FORCE_VORTEX_FIELD)
		elif isinstance(instance, name_type_map['NiPSTurbulenceFieldForce']):
			yield 'type', name_type_map['PSForceType'], (0, None), (False, name_type_map['PSForceType'].FORCE_TURBULENCE_FIELD)
		elif isinstance(instance, name_type_map['NiPSRadialFieldForce']):
			yield 'type', name_type_map['PSForceType'], (0, None), (False, name_type_map['PSForceType'].FORCE_RADIAL_FIELD)
		elif isinstance(instance, name_type_map['NiPSGravityFieldForce']):
			yield 'type', name_type_map['PSForceType'], (0, None), (False, name_type_map['PSForceType'].FORCE_GRAVITY_FIELD)
		elif isinstance(instance, name_type_map['NiPSDragFieldForce']):
			yield 'type', name_type_map['PSForceType'], (0, None), (False, name_type_map['PSForceType'].FORCE_DRAG_FIELD)
		elif isinstance(instance, name_type_map['NiPSAirFieldForce']):
			yield 'type', name_type_map['PSForceType'], (0, None), (False, name_type_map['PSForceType'].FORCE_AIR_FIELD)
		elif isinstance(instance, name_type_map['NiPSDragForce']):
			yield 'type', name_type_map['PSForceType'], (0, None), (False, name_type_map['PSForceType'].FORCE_DRAG)
		elif isinstance(instance, name_type_map['NiPSBombForce']):
			yield 'type', name_type_map['PSForceType'], (0, None), (False, name_type_map['PSForceType'].FORCE_BOMB)
		else:
			yield 'type', name_type_map['PSForceType'], (0, None), (False, None)
		yield 'active', name_type_map['Bool'], (0, None), (False, None)
