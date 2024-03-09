from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimesh.niobjects.NiMeshModifier import NiMeshModifier


class NiMorphMeshModifier(NiMeshModifier):

	"""
	Performs linear-weighted blending between a set of target data streams.
	"""

	__name__ = 'NiMorphMeshModifier'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# FLAG_RELATIVETARGETS = 0x01
		# FLAG_UPDATENORMALS   = 0x02
		# FLAG_NEEDSUPDATE     = 0x04
		# FLAG_ALWAYSUPDATE    = 0x08
		# FLAG_NEEDSCOMPLETION = 0x10
		# FLAG_SKINNED         = 0x20
		# FLAG_SWSKINNED       = 0x40
		self.flags = name_type_map['Byte'](self.context, 0, None)

		# The number of morph targets.
		self.num_targets = name_type_map['Ushort'](self.context, 0, None)

		# The number of morphing data stream elements.
		self.num_elements = name_type_map['Uint'](self.context, 0, None)

		# Semantics and normalization of the morphing data stream elements.
		self.elements = Array(self.context, 0, None, (0,), name_type_map['ElementReference'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'flags', name_type_map['Byte'], (0, None), (False, None), (None, None)
		yield 'num_targets', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'num_elements', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'elements', Array, (0, None, (None,), name_type_map['ElementReference']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'flags', name_type_map['Byte'], (0, None), (False, None)
		yield 'num_targets', name_type_map['Ushort'], (0, None), (False, None)
		yield 'num_elements', name_type_map['Uint'], (0, None), (False, None)
		yield 'elements', Array, (0, None, (instance.num_elements,), name_type_map['ElementReference']), (False, None)
