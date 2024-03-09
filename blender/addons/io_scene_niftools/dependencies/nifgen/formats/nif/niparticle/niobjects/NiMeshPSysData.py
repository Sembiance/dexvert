from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.niparticle.niobjects.NiPSysData import NiPSysData


class NiMeshPSysData(NiPSysData):

	"""
	Particle meshes data.
	"""

	__name__ = 'NiMeshPSysData'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.default_pool_size = name_type_map['Uint'](self.context, 0, None)
		self.fill_pools_on_load = name_type_map['Bool'](self.context, 0, None)
		self.num_generations = name_type_map['Uint'](self.context, 0, None)
		self.generations = Array(self.context, 0, None, (0,), name_type_map['Uint'])
		self.particle_meshes = name_type_map['Ref'](self.context, 0, name_type_map['NiNode'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'default_pool_size', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.version >= 167903232, None)
		yield 'fill_pools_on_load', name_type_map['Bool'], (0, None), (False, None), (lambda context: context.version >= 167903232, None)
		yield 'num_generations', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.version >= 167903232, None)
		yield 'generations', Array, (0, None, (None,), name_type_map['Uint']), (False, None), (lambda context: context.version >= 167903232, None)
		yield 'particle_meshes', name_type_map['Ref'], (0, name_type_map['NiNode']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		if instance.context.version >= 167903232:
			yield 'default_pool_size', name_type_map['Uint'], (0, None), (False, None)
			yield 'fill_pools_on_load', name_type_map['Bool'], (0, None), (False, None)
			yield 'num_generations', name_type_map['Uint'], (0, None), (False, None)
			yield 'generations', Array, (0, None, (instance.num_generations,), name_type_map['Uint']), (False, None)
		yield 'particle_meshes', name_type_map['Ref'], (0, name_type_map['NiNode']), (False, None)
