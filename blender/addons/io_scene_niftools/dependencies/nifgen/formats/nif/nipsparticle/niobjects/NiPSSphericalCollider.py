from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nipsparticle.niobjects.NiPSCollider import NiPSCollider


class NiPSSphericalCollider(NiPSCollider):

	"""
	A spherical collider for particles.
	"""

	__name__ = 'NiPSSphericalCollider'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.radius = name_type_map['Float'].from_value(1.0)
		self.collider_object = name_type_map['Ptr'](self.context, 0, name_type_map['NiAVObject'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'radius', name_type_map['Float'], (0, None), (False, 1.0), (None, None)
		yield 'collider_object', name_type_map['Ptr'], (0, name_type_map['NiAVObject']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'radius', name_type_map['Float'], (0, None), (False, 1.0)
		yield 'collider_object', name_type_map['Ptr'], (0, name_type_map['NiAVObject']), (False, None)
