from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nipsparticle.niobjects.NiPSSimulatorStep import NiPSSimulatorStep


class NiPSSimulatorForcesStep(NiPSSimulatorStep):

	"""
	Encapsulates a floodgate kernel that simulates particle forces.
	"""

	__name__ = 'NiPSSimulatorForcesStep'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.num_forces = name_type_map['Uint'](self.context, 0, None)

		# The forces affecting the particle system.
		self.forces = Array(self.context, 0, name_type_map['NiPSForce'], (0,), name_type_map['Ref'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'num_forces', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'forces', Array, (0, name_type_map['NiPSForce'], (None,), name_type_map['Ref']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'num_forces', name_type_map['Uint'], (0, None), (False, None)
		yield 'forces', Array, (0, name_type_map['NiPSForce'], (instance.num_forces,), name_type_map['Ref']), (False, None)
