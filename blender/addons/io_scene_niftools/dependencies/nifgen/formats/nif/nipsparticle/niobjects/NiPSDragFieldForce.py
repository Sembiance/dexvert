from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nipsparticle.niobjects.NiPSFieldForce import NiPSFieldForce


class NiPSDragFieldForce(NiPSFieldForce):

	"""
	Inside a field, updates particle velocity to simulate the effects of drag.
	"""

	__name__ = 'NiPSDragFieldForce'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.use_direction = name_type_map['Bool'](self.context, 0, None)
		self.direction = name_type_map['Vector3'].from_value((1.0, 0.0, 0.0))
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'use_direction', name_type_map['Bool'], (0, None), (False, None), (None, None)
		yield 'direction', name_type_map['Vector3'], (0, None), (False, (1.0, 0.0, 0.0)), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'use_direction', name_type_map['Bool'], (0, None), (False, None)
		yield 'direction', name_type_map['Vector3'], (0, None), (False, (1.0, 0.0, 0.0))
