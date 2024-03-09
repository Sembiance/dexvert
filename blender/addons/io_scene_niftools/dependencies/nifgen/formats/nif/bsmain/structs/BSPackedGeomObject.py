from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class BSPackedGeomObject(BaseStruct):

	"""
	This is the data necessary to access the shared geometry in a PSG/CSG file.
	"""

	__name__ = 'BSPackedGeomObject'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# BSCRC32 of the filename without the PSG/CSG extension.
		self.filename_hash = name_type_map['Uint'](self.context, 0, None)

		# Offset of the geometry data in the PSG/CSG file.
		self.data_offset = name_type_map['Uint'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'filename_hash', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'data_offset', name_type_map['Uint'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'filename_hash', name_type_map['Uint'], (0, None), (False, None)
		yield 'data_offset', name_type_map['Uint'], (0, None), (False, None)
