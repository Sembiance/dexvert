from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.niparticle.niobjects.NiPSysFieldModifier import NiPSysFieldModifier


class NiPSysGravityFieldModifier(NiPSysFieldModifier):

	"""
	Particle system modifier, implements a gravity field force for particles.
	"""

	__name__ = 'NiPSysGravityFieldModifier'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# Direction of the gravity field in Field Object's space.
		self.direction = name_type_map['Vector3'].from_value((0.0, -1.0, 0.0))
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'direction', name_type_map['Vector3'], (0, None), (False, (0.0, -1.0, 0.0)), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'direction', name_type_map['Vector3'], (0, None), (False, (0.0, -1.0, 0.0))
