from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiParticles import NiParticles


class NiParticleSystem(NiParticles):

	"""
	A particle system.
	Contains members to mimic inheritance shifts for Bethesda 20.2, where NiParticles switched to inheriting BSGeometry.
	Until inheritance shifts are supported, the members are on NiParticleSystem instead of NiParticles for module reasons.
	"""

	__name__ = 'NiParticleSystem'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.vertex_desc = name_type_map['BSVertexDesc'](self.context, 0, None)
		self.far_begin = name_type_map['Ushort'](self.context, 0, None)
		self.far_end = name_type_map['Ushort'](self.context, 0, None)
		self.near_begin = name_type_map['Ushort'](self.context, 0, None)
		self.near_end = name_type_map['Ushort'](self.context, 0, None)
		self.data = name_type_map['Ref'](self.context, 0, name_type_map['NiPSysData'])

		# If true, Particles are birthed into world space.  If false, Particles are birthed into object space.
		self.world_space = name_type_map['Bool'].from_value(True)

		# The number of modifier references.
		self.num_modifiers = name_type_map['Uint'](self.context, 0, None)

		# The list of particle modifiers.
		self.modifiers = Array(self.context, 0, name_type_map['NiPSysModifier'], (0,), name_type_map['Ref'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'vertex_desc', name_type_map['BSVertexDesc'], (0, None), (False, None), (lambda context: context.bs_header.bs_version >= 100, None)
		yield 'far_begin', name_type_map['Ushort'], (0, None), (False, None), (lambda context: context.bs_header.bs_version >= 83, None)
		yield 'far_end', name_type_map['Ushort'], (0, None), (False, None), (lambda context: context.bs_header.bs_version >= 83, None)
		yield 'near_begin', name_type_map['Ushort'], (0, None), (False, None), (lambda context: context.bs_header.bs_version >= 83, None)
		yield 'near_end', name_type_map['Ushort'], (0, None), (False, None), (lambda context: context.bs_header.bs_version >= 83, None)
		yield 'data', name_type_map['Ref'], (0, name_type_map['NiPSysData']), (False, None), (lambda context: context.bs_header.bs_version >= 100, None)
		yield 'world_space', name_type_map['Bool'], (0, None), (False, True), (lambda context: context.version >= 167837696, None)
		yield 'num_modifiers', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.version >= 167837696, None)
		yield 'modifiers', Array, (0, name_type_map['NiPSysModifier'], (None,), name_type_map['Ref']), (False, None), (lambda context: context.version >= 167837696, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		if instance.context.bs_header.bs_version >= 100:
			yield 'vertex_desc', name_type_map['BSVertexDesc'], (0, None), (False, None)
		if instance.context.bs_header.bs_version >= 83:
			yield 'far_begin', name_type_map['Ushort'], (0, None), (False, None)
			yield 'far_end', name_type_map['Ushort'], (0, None), (False, None)
			yield 'near_begin', name_type_map['Ushort'], (0, None), (False, None)
			yield 'near_end', name_type_map['Ushort'], (0, None), (False, None)
		if instance.context.bs_header.bs_version >= 100:
			yield 'data', name_type_map['Ref'], (0, name_type_map['NiPSysData']), (False, None)
		if instance.context.version >= 167837696:
			yield 'world_space', name_type_map['Bool'], (0, None), (False, True)
			yield 'num_modifiers', name_type_map['Uint'], (0, None), (False, None)
			yield 'modifiers', Array, (0, name_type_map['NiPSysModifier'], (instance.num_modifiers,), name_type_map['Ref']), (False, None)
