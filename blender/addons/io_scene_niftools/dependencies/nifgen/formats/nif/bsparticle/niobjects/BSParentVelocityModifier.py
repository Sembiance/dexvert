from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.niparticle.niobjects.NiPSysModifier import NiPSysModifier


class BSParentVelocityModifier(NiPSysModifier):

	"""
	Particle modifier that adds a percentage of object space translation and rotation to particles born in world space.
	"""

	__name__ = 'BSParentVelocityModifier'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# Amount of blending?
		self.damping = name_type_map['Float'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'damping', name_type_map['Float'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'damping', name_type_map['Float'], (0, None), (False, None)
