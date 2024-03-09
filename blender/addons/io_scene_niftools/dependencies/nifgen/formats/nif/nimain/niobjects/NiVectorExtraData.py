from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiExtraData import NiExtraData


class NiVectorExtraData(NiExtraData):

	"""
	DEPRECATED (20.5).
	Extra data in the form of a vector (as x, y, z, w components).
	"""

	__name__ = 'NiVectorExtraData'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# The vector data.
		self.vector_data = name_type_map['Vector4'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'vector_data', name_type_map['Vector4'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'vector_data', name_type_map['Vector4'], (0, None), (False, None)
