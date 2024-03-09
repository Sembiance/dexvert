from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class HalfTexCoord(BaseStruct):

	"""
	Texture coordinates (u,v).
	"""

	__name__ = 'HalfTexCoord'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# First coordinate.
		self.u = name_type_map['Hfloat'](self.context, 0, None)

		# Second coordinate.
		self.v = name_type_map['Hfloat'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'u', name_type_map['Hfloat'], (0, None), (False, None), (None, None)
		yield 'v', name_type_map['Hfloat'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'u', name_type_map['Hfloat'], (0, None), (False, None)
		yield 'v', name_type_map['Hfloat'], (0, None), (False, None)
