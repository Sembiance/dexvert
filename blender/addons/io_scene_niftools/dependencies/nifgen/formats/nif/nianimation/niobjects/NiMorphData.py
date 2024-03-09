from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiObject import NiObject


class NiMorphData(NiObject):

	"""
	DEPRECATED (20.5), replaced by NiMorphMeshModifier.
	Geometry morphing data.
	"""

	__name__ = 'NiMorphData'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# Number of morphing object.
		self.num_morphs = name_type_map['Uint'](self.context, 0, None)

		# Number of vertices.
		self.num_vertices = name_type_map['Uint'](self.context, 0, None)

		# This byte is always 1 in all official files.
		self.relative_targets = name_type_map['Byte'].from_value(1)

		# The geometry morphing objects.
		self.morphs = Array(self.context, self.num_vertices, None, (0,), name_type_map['Morph'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'num_morphs', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'num_vertices', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'relative_targets', name_type_map['Byte'], (0, None), (False, 1), (None, None)
		yield 'morphs', Array, (None, None, (None,), name_type_map['Morph']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'num_morphs', name_type_map['Uint'], (0, None), (False, None)
		yield 'num_vertices', name_type_map['Uint'], (0, None), (False, None)
		yield 'relative_targets', name_type_map['Byte'], (0, None), (False, 1)
		yield 'morphs', Array, (instance.num_vertices, None, (instance.num_morphs,), name_type_map['Morph']), (False, None)
	def apply_scale(self, scale):
		"""Apply scale factor on data."""
		super().apply_scale(scale)
		for morph in self.morphs:
			for v in morph.vectors:
				v.x *= scale
				v.y *= scale
				v.z *= scale

