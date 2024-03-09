from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiObject import NiObject


class BhkPoseArray(NiObject):

	"""
	Found in Fallout 3 .psa files, extra ragdoll info for NPCs/creatures. (usually idleanims\deathposes.psa)
	Defines different kill poses. The game selects the pose randomly and applies it to a skeleton immediately upon ragdolling.
	Poses can be previewed in GECK Object Window-Actor Data-Ragdoll and selecting Pose Matching tab.
	"""

	__name__ = 'bhkPoseArray'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.num_bones = name_type_map['Uint'](self.context, 0, None)
		self.bones = Array(self.context, 0, None, (0,), name_type_map['NiFixedString'])
		self.num_poses = name_type_map['Uint'](self.context, 0, None)
		self.poses = Array(self.context, 0, None, (0,), name_type_map['BonePose'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'num_bones', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'bones', Array, (0, None, (None,), name_type_map['NiFixedString']), (False, None), (None, None)
		yield 'num_poses', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'poses', Array, (0, None, (None,), name_type_map['BonePose']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'num_bones', name_type_map['Uint'], (0, None), (False, None)
		yield 'bones', Array, (0, None, (instance.num_bones,), name_type_map['NiFixedString']), (False, None)
		yield 'num_poses', name_type_map['Uint'], (0, None), (False, None)
		yield 'poses', Array, (0, None, (instance.num_poses,), name_type_map['BonePose']), (False, None)
