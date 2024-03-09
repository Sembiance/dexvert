from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nilegacy.niobjects.NiParticleModifier import NiParticleModifier


class NiGravity(NiParticleModifier):

	"""
	LEGACY (pre-10.1) particle modifier. Applies a gravitational field on the particles.
	"""

	__name__ = 'NiGravity'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.decay = name_type_map['Float'](self.context, 0, None)

		# The strength/force of this gravity.
		self.force = name_type_map['Float'](self.context, 0, None)

		# The force field type.
		self.type = name_type_map['FieldType'](self.context, 0, None)

		# The position of the mass point relative to the particle system.
		self.position = name_type_map['Vector3'](self.context, 0, None)

		# The direction of the applied acceleration.
		self.direction = name_type_map['Vector3'](self.context, 0, None)
		self.unknown_01 = name_type_map['Float'](self.context, 0, None)
		self.unknown_02 = name_type_map['Float'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'decay', name_type_map['Float'], (0, None), (False, None), (lambda context: context.version >= 50528269, None)
		yield 'force', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'type', name_type_map['FieldType'], (0, None), (False, None), (None, None)
		yield 'position', name_type_map['Vector3'], (0, None), (False, None), (None, None)
		yield 'direction', name_type_map['Vector3'], (0, None), (False, None), (None, None)
		yield 'unknown_01', name_type_map['Float'], (0, None), (False, None), (lambda context: context.version <= 33751040, None)
		yield 'unknown_02', name_type_map['Float'], (0, None), (False, None), (lambda context: context.version <= 33751040, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		if instance.context.version >= 50528269:
			yield 'decay', name_type_map['Float'], (0, None), (False, None)
		yield 'force', name_type_map['Float'], (0, None), (False, None)
		yield 'type', name_type_map['FieldType'], (0, None), (False, None)
		yield 'position', name_type_map['Vector3'], (0, None), (False, None)
		yield 'direction', name_type_map['Vector3'], (0, None), (False, None)
		if instance.context.version <= 33751040:
			yield 'unknown_01', name_type_map['Float'], (0, None), (False, None)
			yield 'unknown_02', name_type_map['Float'], (0, None), (False, None)
