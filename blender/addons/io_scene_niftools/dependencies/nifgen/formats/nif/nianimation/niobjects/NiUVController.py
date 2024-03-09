from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiTimeController import NiTimeController


class NiUVController(NiTimeController):

	"""
	DEPRECATED (pre-10.1), REMOVED (20.3).
	Time controller for texture coordinates.
	"""

	__name__ = 'NiUVController'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.texture_set = name_type_map['Ushort'](self.context, 0, None)

		# Texture coordinate controller data index.
		self.data = name_type_map['Ref'](self.context, 0, name_type_map['NiUVData'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'texture_set', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'data', name_type_map['Ref'], (0, name_type_map['NiUVData']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'texture_set', name_type_map['Ushort'], (0, None), (False, None)
		yield 'data', name_type_map['Ref'], (0, name_type_map['NiUVData']), (False, None)
