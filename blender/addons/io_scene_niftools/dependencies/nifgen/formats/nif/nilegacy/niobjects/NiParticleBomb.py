from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nilegacy.niobjects.NiParticleModifier import NiParticleModifier


class NiParticleBomb(NiParticleModifier):

	"""
	LEGACY (pre-10.1) particle modifier.
	"""

	__name__ = 'NiParticleBomb'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.decay = name_type_map['Float'](self.context, 0, None)
		self.duration = name_type_map['Float'](self.context, 0, None)
		self.delta_v = name_type_map['Float'](self.context, 0, None)
		self.start = name_type_map['Float'](self.context, 0, None)
		self.decay_type = name_type_map['DecayType'](self.context, 0, None)
		self.symmetry_type = name_type_map['SymmetryType'](self.context, 0, None)

		# The position of the mass point relative to the particle system?
		self.position = name_type_map['Vector3'](self.context, 0, None)

		# The direction of the applied acceleration?
		self.direction = name_type_map['Vector3'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'decay', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'duration', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'delta_v', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'start', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'decay_type', name_type_map['DecayType'], (0, None), (False, None), (None, None)
		yield 'symmetry_type', name_type_map['SymmetryType'], (0, None), (False, None), (lambda context: context.version >= 67174412, None)
		yield 'position', name_type_map['Vector3'], (0, None), (False, None), (None, None)
		yield 'direction', name_type_map['Vector3'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'decay', name_type_map['Float'], (0, None), (False, None)
		yield 'duration', name_type_map['Float'], (0, None), (False, None)
		yield 'delta_v', name_type_map['Float'], (0, None), (False, None)
		yield 'start', name_type_map['Float'], (0, None), (False, None)
		yield 'decay_type', name_type_map['DecayType'], (0, None), (False, None)
		if instance.context.version >= 67174412:
			yield 'symmetry_type', name_type_map['SymmetryType'], (0, None), (False, None)
		yield 'position', name_type_map['Vector3'], (0, None), (False, None)
		yield 'direction', name_type_map['Vector3'], (0, None), (False, None)
