from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiTimeController import NiTimeController


class NiControllerManager(NiTimeController):

	"""
	Controls animation sequences on a specific branch of the scene graph.
	"""

	__name__ = 'NiControllerManager'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# Whether transformation accumulation is enabled. If accumulation is not enabled, the manager will treat all sequence data on the accumulation root as absolute data instead of relative delta values.
		self.cumulative = name_type_map['Bool'](self.context, 0, None)
		self.num_controller_sequences = name_type_map['Uint'](self.context, 0, None)
		self.controller_sequences = Array(self.context, 0, name_type_map['NiControllerSequence'], (0,), name_type_map['Ref'])
		self.object_palette = name_type_map['Ref'](self.context, 0, name_type_map['NiDefaultAVObjectPalette'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'cumulative', name_type_map['Bool'], (0, None), (False, None), (None, None)
		yield 'num_controller_sequences', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'controller_sequences', Array, (0, name_type_map['NiControllerSequence'], (None,), name_type_map['Ref']), (False, None), (None, None)
		yield 'object_palette', name_type_map['Ref'], (0, name_type_map['NiDefaultAVObjectPalette']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'cumulative', name_type_map['Bool'], (0, None), (False, None)
		yield 'num_controller_sequences', name_type_map['Uint'], (0, None), (False, None)
		yield 'controller_sequences', Array, (0, name_type_map['NiControllerSequence'], (instance.num_controller_sequences,), name_type_map['Ref']), (False, None)
		yield 'object_palette', name_type_map['Ref'], (0, name_type_map['NiDefaultAVObjectPalette']), (False, None)
