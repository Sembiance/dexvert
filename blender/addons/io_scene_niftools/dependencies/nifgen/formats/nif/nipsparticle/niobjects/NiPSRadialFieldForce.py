from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nipsparticle.niobjects.NiPSFieldForce import NiPSFieldForce


class NiPSRadialFieldForce(NiPSFieldForce):

	"""
	Inside a field, updates particle velocity to simulate the effects of point gravity.
	"""

	__name__ = 'NiPSRadialFieldForce'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.radial_factor = name_type_map['Float'](self.context, 0, None)
		self.dem_unknown_int = name_type_map['Uint'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'radial_factor', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'dem_unknown_int', name_type_map['Uint'], (0, None), (False, None), (lambda context: 335938816 <= context.version <= 335938816 and context.user_version >= 14, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'radial_factor', name_type_map['Float'], (0, None), (False, None)
		if 335938816 <= instance.context.version <= 335938816 and instance.context.user_version >= 14:
			yield 'dem_unknown_int', name_type_map['Uint'], (0, None), (False, None)
