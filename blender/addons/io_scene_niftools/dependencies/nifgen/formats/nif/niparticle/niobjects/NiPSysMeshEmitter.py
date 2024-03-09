from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.niparticle.niobjects.NiPSysEmitter import NiPSysEmitter


class NiPSysMeshEmitter(NiPSysEmitter):

	"""
	Particle emitter that uses points on a specified mesh to emit from.
	"""

	__name__ = 'NiPSysMeshEmitter'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.num_emitter_meshes = name_type_map['Uint'](self.context, 0, None)

		# The meshes which are emitted from.
		self.emitter_meshes = Array(self.context, 0, name_type_map['NiAVObject'], (0,), name_type_map['Ptr'])

		# The method by which the initial particle velocity will be computed.
		self.initial_velocity_type = name_type_map['VelocityType'](self.context, 0, None)

		# The manner in which particles are emitted from the Emitter Meshes.
		self.emission_type = name_type_map['EmitFrom'](self.context, 0, None)

		# The emission axis if VELOCITY_USE_DIRECTION.
		self.emission_axis = name_type_map['Vector3'].from_value((1.0, 0.0, 0.0))
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'num_emitter_meshes', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'emitter_meshes', Array, (0, name_type_map['NiAVObject'], (None,), name_type_map['Ptr']), (False, None), (None, None)
		yield 'initial_velocity_type', name_type_map['VelocityType'], (0, None), (False, None), (None, None)
		yield 'emission_type', name_type_map['EmitFrom'], (0, None), (False, None), (None, None)
		yield 'emission_axis', name_type_map['Vector3'], (0, None), (False, (1.0, 0.0, 0.0)), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'num_emitter_meshes', name_type_map['Uint'], (0, None), (False, None)
		yield 'emitter_meshes', Array, (0, name_type_map['NiAVObject'], (instance.num_emitter_meshes,), name_type_map['Ptr']), (False, None)
		yield 'initial_velocity_type', name_type_map['VelocityType'], (0, None), (False, None)
		yield 'emission_type', name_type_map['EmitFrom'], (0, None), (False, None)
		yield 'emission_axis', name_type_map['Vector3'], (0, None), (False, (1.0, 0.0, 0.0))
