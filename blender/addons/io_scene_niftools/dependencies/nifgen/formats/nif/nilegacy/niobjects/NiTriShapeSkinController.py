from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiTimeController import NiTimeController


class NiTriShapeSkinController(NiTimeController):

	"""
	Old version of skinning instance.
	"""

	__name__ = 'NiTriShapeSkinController'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# The number of node bones referenced as influences.
		self.num_bones = name_type_map['Uint'](self.context, 0, None)

		# The number of vertex weights stored for each bone.
		self.vertex_counts = Array(self.context, 0, None, (0,), name_type_map['Uint'])

		# List of all armature bones.
		self.bones = Array(self.context, 0, name_type_map['NiBone'], (0,), name_type_map['Ptr'])

		# Contains skin weight data for each node that this skin is influenced by.
		self.bone_data = Array(self.context, 0, None, (0,), name_type_map['OldSkinData'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'num_bones', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'vertex_counts', Array, (0, None, (None,), name_type_map['Uint']), (False, None), (None, None)
		yield 'bones', Array, (0, name_type_map['NiBone'], (None,), name_type_map['Ptr']), (False, None), (None, None)
		yield 'bone_data', Array, (0, None, (None, None,), name_type_map['OldSkinData']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'num_bones', name_type_map['Uint'], (0, None), (False, None)
		yield 'vertex_counts', Array, (0, None, (instance.num_bones,), name_type_map['Uint']), (False, None)
		yield 'bones', Array, (0, name_type_map['NiBone'], (instance.num_bones,), name_type_map['Ptr']), (False, None)
		yield 'bone_data', Array, (0, None, (instance.num_bones, instance.vertex_counts,), name_type_map['OldSkinData']), (False, None)
