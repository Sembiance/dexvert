from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiTriBasedGeom import NiTriBasedGeom


class BSLODTriShape(NiTriBasedGeom):

	"""
	A variation on NiTriShape, for visibility control over vertex groups.
	"""

	__name__ = 'BSLODTriShape'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.lod_0_size = name_type_map['Uint'](self.context, 0, None)
		self.lod_1_size = name_type_map['Uint'](self.context, 0, None)
		self.lod_2_size = name_type_map['Uint'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'lod_0_size', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'lod_1_size', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'lod_2_size', name_type_map['Uint'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'lod_0_size', name_type_map['Uint'], (0, None), (False, None)
		yield 'lod_1_size', name_type_map['Uint'], (0, None), (False, None)
		yield 'lod_2_size', name_type_map['Uint'], (0, None), (False, None)
