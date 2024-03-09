from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nipsparticle.niobjects.NiPSForce import NiPSForce


class NiPSGravityForce(NiPSForce):

	"""
	Applies a gravitational force to particles.
	"""

	__name__ = 'NiPSGravityForce'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.gravity_axis = name_type_map['Vector3'].from_value((1.0, 0.0, 0.0))
		self.decay = name_type_map['Float'](self.context, 0, None)
		self.strength = name_type_map['Float'](self.context, 0, None)
		self.force_type = name_type_map['ForceType'](self.context, 0, None)
		self.turbulence = name_type_map['Float'](self.context, 0, None)
		self.turbulence_scale = name_type_map['Float'].from_value(1.0)
		self.gravity_object = name_type_map['Ptr'](self.context, 0, name_type_map['NiAVObject'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'gravity_axis', name_type_map['Vector3'], (0, None), (False, (1.0, 0.0, 0.0)), (None, None)
		yield 'decay', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'strength', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'force_type', name_type_map['ForceType'], (0, None), (False, None), (None, None)
		yield 'turbulence', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'turbulence_scale', name_type_map['Float'], (0, None), (False, 1.0), (None, None)
		yield 'gravity_object', name_type_map['Ptr'], (0, name_type_map['NiAVObject']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'gravity_axis', name_type_map['Vector3'], (0, None), (False, (1.0, 0.0, 0.0))
		yield 'decay', name_type_map['Float'], (0, None), (False, None)
		yield 'strength', name_type_map['Float'], (0, None), (False, None)
		yield 'force_type', name_type_map['ForceType'], (0, None), (False, None)
		yield 'turbulence', name_type_map['Float'], (0, None), (False, None)
		yield 'turbulence_scale', name_type_map['Float'], (0, None), (False, 1.0)
		yield 'gravity_object', name_type_map['Ptr'], (0, name_type_map['NiAVObject']), (False, None)
