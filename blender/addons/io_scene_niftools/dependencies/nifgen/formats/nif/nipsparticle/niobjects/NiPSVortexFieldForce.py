from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nipsparticle.niobjects.NiPSFieldForce import NiPSFieldForce


class NiPSVortexFieldForce(NiPSFieldForce):

	"""
	Inside a field, updates particle velocity to simulate the effects of a vortex.
	"""

	__name__ = 'NiPSVortexFieldForce'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.direction = name_type_map['Vector3'].from_value((1.0, 0.0, 0.0))
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'direction', name_type_map['Vector3'], (0, None), (False, (1.0, 0.0, 0.0)), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'direction', name_type_map['Vector3'], (0, None), (False, (1.0, 0.0, 0.0))
