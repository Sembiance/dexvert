from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nipsparticle.niobjects.NiPSFieldForce import NiPSFieldForce


class NiPSGravityFieldForce(NiPSFieldForce):

	"""
	Inside a field, updates particle velocity to simulate the effects of directional gravity.
	"""

	__name__ = 'NiPSGravityFieldForce'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.dem_unknown_short = name_type_map['Ushort'](self.context, 0, None)
		self.direction = name_type_map['Vector3'].from_value((1.0, 0.0, 0.0))
		self.dem_unknown_byte = name_type_map['Byte'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'dem_unknown_short', name_type_map['Ushort'], (0, None), (False, None), (lambda context: 335938816 <= context.version <= 335938816 and context.user_version >= 14, None)
		yield 'direction', name_type_map['Vector3'], (0, None), (False, (1.0, 0.0, 0.0)), (None, None)
		yield 'dem_unknown_byte', name_type_map['Byte'], (0, None), (False, None), (lambda context: 335938816 <= context.version <= 335938816 and context.user_version >= 14, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		if 335938816 <= instance.context.version <= 335938816 and instance.context.user_version >= 14:
			yield 'dem_unknown_short', name_type_map['Ushort'], (0, None), (False, None)
		yield 'direction', name_type_map['Vector3'], (0, None), (False, (1.0, 0.0, 0.0))
		if 335938816 <= instance.context.version <= 335938816 and instance.context.user_version >= 14:
			yield 'dem_unknown_byte', name_type_map['Byte'], (0, None), (False, None)
