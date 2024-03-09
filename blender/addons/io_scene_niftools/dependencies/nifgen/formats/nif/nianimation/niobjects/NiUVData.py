from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiObject import NiObject


class NiUVData(NiObject):

	"""
	DEPRECATED (pre-10.1), REMOVED (20.3)
	Texture coordinate data.
	"""

	__name__ = 'NiUVData'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# Four UV data groups. Appear to be U translation, V translation, U scaling/tiling, V scaling/tiling.
		self.uv_groups = Array(self.context, 0, name_type_map['Float'], (0,), name_type_map['KeyGroup'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'uv_groups', Array, (0, name_type_map['Float'], (4,), name_type_map['KeyGroup']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'uv_groups', Array, (0, name_type_map['Float'], (4,), name_type_map['KeyGroup']), (False, None)
