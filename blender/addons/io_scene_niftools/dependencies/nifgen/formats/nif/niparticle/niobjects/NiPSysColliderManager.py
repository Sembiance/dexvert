from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.niparticle.niobjects.NiPSysModifier import NiPSysModifier


class NiPSysColliderManager(NiPSysModifier):

	"""
	Particle modifier that adds a defined shape to act as a collision object for particles to interact with.
	"""

	__name__ = 'NiPSysColliderManager'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.collider = name_type_map['Ref'](self.context, 0, name_type_map['NiPSysCollider'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'collider', name_type_map['Ref'], (0, name_type_map['NiPSysCollider']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'collider', name_type_map['Ref'], (0, name_type_map['NiPSysCollider']), (False, None)
