from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimesh.niobjects.NiMeshModifier import NiMeshModifier


class NiPSSimulator(NiMeshModifier):

	"""
	The mesh modifier that performs all particle system simulation.
	"""

	__name__ = 'NiPSSimulator'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.num_simulation_steps = name_type_map['Uint'](self.context, 0, None)
		self.simulation_steps = Array(self.context, 0, name_type_map['NiPSSimulatorStep'], (0,), name_type_map['Ref'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'num_simulation_steps', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'simulation_steps', Array, (0, name_type_map['NiPSSimulatorStep'], (None,), name_type_map['Ref']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'num_simulation_steps', name_type_map['Uint'], (0, None), (False, None)
		yield 'simulation_steps', Array, (0, name_type_map['NiPSSimulatorStep'], (instance.num_simulation_steps,), name_type_map['Ref']), (False, None)
