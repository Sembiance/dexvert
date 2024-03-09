from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiObject import NiObject


class NiPhysXBodyDesc(NiObject):

	"""
	For serializing NxBodyDesc objects.
	"""

	__name__ = 'NiPhysXBodyDesc'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.local_pose = name_type_map['Matrix34'](self.context, 0, None)
		self.space_inertia = name_type_map['Vector3'](self.context, 0, None)
		self.mass = name_type_map['Float'](self.context, 0, None)
		self.num_vels = name_type_map['Uint'](self.context, 0, None)
		self.vels = Array(self.context, 0, None, (0,), name_type_map['PhysXBodyStoredVels'])
		self.wake_up_counter = name_type_map['Float'].from_value(0.4)
		self.linear_damping = name_type_map['Float'](self.context, 0, None)
		self.angular_damping = name_type_map['Float'].from_value(0.05)
		self.max_angular_velocity = name_type_map['Float'].from_value(-1.0)
		self.ccd_motion_threshold = name_type_map['Float'](self.context, 0, None)
		self.flags = name_type_map['NxBodyFlag'].from_value(2304)
		self.sleep_linear_velocity = name_type_map['Float'].from_value(-1.0)
		self.sleep_angular_velocity = name_type_map['Float'].from_value(-1.0)
		self.solver_iteration_count = name_type_map['Uint'].from_value(4)
		self.sleep_energy_threshold = name_type_map['Float'].from_value(-1.0)
		self.sleep_damping = name_type_map['Float'](self.context, 0, None)
		self.contact_report_threshold = name_type_map['Float'].from_value(3.402823466e+38)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'local_pose', name_type_map['Matrix34'], (0, None), (False, None), (None, None)
		yield 'space_inertia', name_type_map['Vector3'], (0, None), (False, None), (None, None)
		yield 'mass', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'num_vels', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'vels', Array, (0, None, (None,), name_type_map['PhysXBodyStoredVels']), (False, None), (None, None)
		yield 'wake_up_counter', name_type_map['Float'], (0, None), (False, 0.4), (None, None)
		yield 'linear_damping', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'angular_damping', name_type_map['Float'], (0, None), (False, 0.05), (None, None)
		yield 'max_angular_velocity', name_type_map['Float'], (0, None), (False, -1.0), (None, None)
		yield 'ccd_motion_threshold', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'flags', name_type_map['NxBodyFlag'], (0, None), (False, 2304), (None, None)
		yield 'sleep_linear_velocity', name_type_map['Float'], (0, None), (False, -1.0), (None, None)
		yield 'sleep_angular_velocity', name_type_map['Float'], (0, None), (False, -1.0), (None, None)
		yield 'solver_iteration_count', name_type_map['Uint'], (0, None), (False, 4), (None, None)
		yield 'sleep_energy_threshold', name_type_map['Float'], (0, None), (False, -1.0), (lambda context: context.version >= 335740928, None)
		yield 'sleep_damping', name_type_map['Float'], (0, None), (False, None), (lambda context: context.version >= 335740928, None)
		yield 'contact_report_threshold', name_type_map['Float'], (0, None), (False, 3.402823466e+38), (lambda context: context.version >= 335806464, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'local_pose', name_type_map['Matrix34'], (0, None), (False, None)
		yield 'space_inertia', name_type_map['Vector3'], (0, None), (False, None)
		yield 'mass', name_type_map['Float'], (0, None), (False, None)
		yield 'num_vels', name_type_map['Uint'], (0, None), (False, None)
		yield 'vels', Array, (0, None, (instance.num_vels,), name_type_map['PhysXBodyStoredVels']), (False, None)
		yield 'wake_up_counter', name_type_map['Float'], (0, None), (False, 0.4)
		yield 'linear_damping', name_type_map['Float'], (0, None), (False, None)
		yield 'angular_damping', name_type_map['Float'], (0, None), (False, 0.05)
		yield 'max_angular_velocity', name_type_map['Float'], (0, None), (False, -1.0)
		yield 'ccd_motion_threshold', name_type_map['Float'], (0, None), (False, None)
		yield 'flags', name_type_map['NxBodyFlag'], (0, None), (False, 2304)
		yield 'sleep_linear_velocity', name_type_map['Float'], (0, None), (False, -1.0)
		yield 'sleep_angular_velocity', name_type_map['Float'], (0, None), (False, -1.0)
		yield 'solver_iteration_count', name_type_map['Uint'], (0, None), (False, 4)
		if instance.context.version >= 335740928:
			yield 'sleep_energy_threshold', name_type_map['Float'], (0, None), (False, -1.0)
			yield 'sleep_damping', name_type_map['Float'], (0, None), (False, None)
		if instance.context.version >= 335806464:
			yield 'contact_report_threshold', name_type_map['Float'], (0, None), (False, 3.402823466e+38)
