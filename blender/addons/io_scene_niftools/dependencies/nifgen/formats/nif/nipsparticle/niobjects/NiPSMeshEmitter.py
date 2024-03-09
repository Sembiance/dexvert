from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nipsparticle.niobjects.NiPSEmitter import NiPSEmitter


class NiPSMeshEmitter(NiPSEmitter):

	"""
	Emits particles from one or more NiMesh objects. A random mesh emitter is selected for each particle emission.
	"""

	__name__ = 'NiPSMeshEmitter'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.num_mesh_emitters = name_type_map['Uint'](self.context, 0, None)
		self.mesh_emitters = Array(self.context, 0, name_type_map['NiMesh'], (0,), name_type_map['Ptr'])
		self.emit_axis = name_type_map['Vector3'](self.context, 0, None)
		self.emitter_object = name_type_map['Ptr'](self.context, 0, name_type_map['NiAVObject'])
		self.mesh_emission_type = name_type_map['EmitFrom'](self.context, 0, None)
		self.initial_velocity_type = name_type_map['VelocityType'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'num_mesh_emitters', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'mesh_emitters', Array, (0, name_type_map['NiMesh'], (None,), name_type_map['Ptr']), (False, None), (None, None)
		yield 'emit_axis', name_type_map['Vector3'], (0, None), (False, None), (lambda context: context.version <= 335937536, None)
		yield 'emitter_object', name_type_map['Ptr'], (0, name_type_map['NiAVObject']), (False, None), (lambda context: context.version >= 335937792, None)
		yield 'mesh_emission_type', name_type_map['EmitFrom'], (0, None), (False, None), (None, None)
		yield 'initial_velocity_type', name_type_map['VelocityType'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'num_mesh_emitters', name_type_map['Uint'], (0, None), (False, None)
		yield 'mesh_emitters', Array, (0, name_type_map['NiMesh'], (instance.num_mesh_emitters,), name_type_map['Ptr']), (False, None)
		if instance.context.version <= 335937536:
			yield 'emit_axis', name_type_map['Vector3'], (0, None), (False, None)
		if instance.context.version >= 335937792:
			yield 'emitter_object', name_type_map['Ptr'], (0, name_type_map['NiAVObject']), (False, None)
		yield 'mesh_emission_type', name_type_map['EmitFrom'], (0, None), (False, None)
		yield 'initial_velocity_type', name_type_map['VelocityType'], (0, None), (False, None)
