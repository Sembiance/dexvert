from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nilegacy.niobjects.NiParticleModifier import NiParticleModifier


class NiParticleRotation(NiParticleModifier):

	"""
	LEGACY (pre-10.1) particle modifier.
	"""

	__name__ = 'NiParticleRotation'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.random_initial_axis = name_type_map['Byte'](self.context, 0, None)
		self.initial_axis = name_type_map['Vector3'](self.context, 0, None)
		self.rotation_speed = name_type_map['Float'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'random_initial_axis', name_type_map['Byte'], (0, None), (False, None), (None, None)
		yield 'initial_axis', name_type_map['Vector3'], (0, None), (False, None), (None, None)
		yield 'rotation_speed', name_type_map['Float'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'random_initial_axis', name_type_map['Byte'], (0, None), (False, None)
		yield 'initial_axis', name_type_map['Vector3'], (0, None), (False, None)
		yield 'rotation_speed', name_type_map['Float'], (0, None), (False, None)
