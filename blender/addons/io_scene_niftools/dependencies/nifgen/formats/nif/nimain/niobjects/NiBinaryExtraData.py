from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiExtraData import NiExtraData


class NiBinaryExtraData(NiExtraData):

	"""
	Binary extra data object. Used to store tangents and bitangents in Oblivion.
	"""

	__name__ = 'NiBinaryExtraData'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# The binary data.
		self.binary_data = name_type_map['ByteArray'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'binary_data', name_type_map['ByteArray'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'binary_data', name_type_map['ByteArray'], (0, None), (False, None)
