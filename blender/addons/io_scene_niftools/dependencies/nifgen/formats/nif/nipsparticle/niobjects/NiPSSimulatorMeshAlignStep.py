from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nipsparticle.niobjects.NiPSSimulatorStep import NiPSSimulatorStep


class NiPSSimulatorMeshAlignStep(NiPSSimulatorStep):

	"""
	Encapsulates a floodgate kernel that updates mesh particle alignment and transforms.
	"""

	__name__ = 'NiPSSimulatorMeshAlignStep'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.num_rotation_keys = name_type_map['Byte'](self.context, 0, None)

		# The particle rotation keys.
		self.rotation_keys = Array(self.context, 1, name_type_map['Quaternion'], (0,), name_type_map['QuatKey'])

		# The loop behavior for the rotation keys.
		self.rotation_loop_behavior = name_type_map['PSLoopBehavior'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'num_rotation_keys', name_type_map['Byte'], (0, None), (False, None), (None, None)
		yield 'rotation_keys', Array, (1, name_type_map['Quaternion'], (None,), name_type_map['QuatKey']), (False, None), (None, None)
		yield 'rotation_loop_behavior', name_type_map['PSLoopBehavior'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'num_rotation_keys', name_type_map['Byte'], (0, None), (False, None)
		yield 'rotation_keys', Array, (1, name_type_map['Quaternion'], (instance.num_rotation_keys,), name_type_map['QuatKey']), (False, None)
		yield 'rotation_loop_behavior', name_type_map['PSLoopBehavior'], (0, None), (False, None)
