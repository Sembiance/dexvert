from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nianimation.niobjects.NiKeyBasedInterpolator import NiKeyBasedInterpolator


class NiBoolInterpolator(NiKeyBasedInterpolator):

	"""
	Uses NiBoolKeys to animate a bool value over time.
	"""

	__name__ = 'NiBoolInterpolator'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# Pose value if lacking NiBoolData.
		self.value = name_type_map['Bool'].from_value(2)
		self.data = name_type_map['Ref'](self.context, 0, name_type_map['NiBoolData'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'value', name_type_map['Bool'], (0, None), (False, 2), (None, None)
		yield 'data', name_type_map['Ref'], (0, name_type_map['NiBoolData']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'value', name_type_map['Bool'], (0, None), (False, 2)
		yield 'data', name_type_map['Ref'], (0, name_type_map['NiBoolData']), (False, None)
