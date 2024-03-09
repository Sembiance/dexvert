from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.niparticle.niobjects.NiPSysModifier import NiPSysModifier


class NiPSysBombModifier(NiPSysModifier):

	"""
	Particle modifier that applies an explosive force to particles.
	"""

	__name__ = 'NiPSysBombModifier'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# The object whose position and orientation are the basis of the force.
		self.bomb_object = name_type_map['Ptr'](self.context, 0, name_type_map['NiNode'])

		# The local direction of the force.
		self.bomb_axis = name_type_map['Vector3'](self.context, 0, None)

		# How the bomb force will decrease with distance.
		self.decay = name_type_map['Float'](self.context, 0, None)

		# The acceleration the bomb will apply to particles.
		self.delta_v = name_type_map['Float'](self.context, 0, None)
		self.decay_type = name_type_map['DecayType'](self.context, 0, None)
		self.symmetry_type = name_type_map['SymmetryType'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'bomb_object', name_type_map['Ptr'], (0, name_type_map['NiNode']), (False, None), (None, None)
		yield 'bomb_axis', name_type_map['Vector3'], (0, None), (False, None), (None, None)
		yield 'decay', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'delta_v', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'decay_type', name_type_map['DecayType'], (0, None), (False, None), (None, None)
		yield 'symmetry_type', name_type_map['SymmetryType'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'bomb_object', name_type_map['Ptr'], (0, name_type_map['NiNode']), (False, None)
		yield 'bomb_axis', name_type_map['Vector3'], (0, None), (False, None)
		yield 'decay', name_type_map['Float'], (0, None), (False, None)
		yield 'delta_v', name_type_map['Float'], (0, None), (False, None)
		yield 'decay_type', name_type_map['DecayType'], (0, None), (False, None)
		yield 'symmetry_type', name_type_map['SymmetryType'], (0, None), (False, None)
