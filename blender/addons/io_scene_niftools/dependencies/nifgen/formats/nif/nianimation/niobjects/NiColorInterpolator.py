from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nianimation.niobjects.NiKeyBasedInterpolator import NiKeyBasedInterpolator


class NiColorInterpolator(NiKeyBasedInterpolator):

	"""
	Animates a color value over time.
	"""

	__name__ = 'NiColorInterpolator'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.value = name_type_map['Color4'].from_value((-3.402823466e+38, -3.402823466e+38, -3.402823466e+38, -3.402823466e+38))
		self.data = name_type_map['Ref'](self.context, 0, name_type_map['NiColorData'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'value', name_type_map['Color4'], (0, None), (False, (-3.402823466e+38, -3.402823466e+38, -3.402823466e+38, -3.402823466e+38)), (None, None)
		yield 'data', name_type_map['Ref'], (0, name_type_map['NiColorData']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'value', name_type_map['Color4'], (0, None), (False, (-3.402823466e+38, -3.402823466e+38, -3.402823466e+38, -3.402823466e+38))
		yield 'data', name_type_map['Ref'], (0, name_type_map['NiColorData']), (False, None)
