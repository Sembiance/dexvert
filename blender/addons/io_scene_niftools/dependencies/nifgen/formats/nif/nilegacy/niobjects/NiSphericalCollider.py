from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nilegacy.niobjects.NiParticleCollider import NiParticleCollider


class NiSphericalCollider(NiParticleCollider):

	"""
	LEGACY (pre-10.1) particle modifier.
	"""

	__name__ = 'NiSphericalCollider'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.radius = name_type_map['Float'](self.context, 0, None)
		self.position = name_type_map['Vector3'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'radius', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'position', name_type_map['Vector3'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'radius', name_type_map['Float'], (0, None), (False, None)
		yield 'position', name_type_map['Vector3'], (0, None), (False, None)
