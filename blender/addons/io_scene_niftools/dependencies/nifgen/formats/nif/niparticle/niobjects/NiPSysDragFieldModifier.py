from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.niparticle.niobjects.NiPSysFieldModifier import NiPSysFieldModifier


class NiPSysDragFieldModifier(NiPSysFieldModifier):

	"""
	Particle system modifier, implements a drag field force for particles.
	"""

	__name__ = 'NiPSysDragFieldModifier'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# Whether or not the drag force applies only in the direction specified.
		self.use_direction = name_type_map['Bool'](self.context, 0, None)

		# Direction in which the force applies if Use Direction is true.
		self.direction = name_type_map['Vector3'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'use_direction', name_type_map['Bool'], (0, None), (False, None), (None, None)
		yield 'direction', name_type_map['Vector3'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'use_direction', name_type_map['Bool'], (0, None), (False, None)
		yield 'direction', name_type_map['Vector3'], (0, None), (False, None)
