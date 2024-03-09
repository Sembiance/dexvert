from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiExtraData import NiExtraData


class BSBehaviorGraphExtraData(NiExtraData):

	"""
	Links a nif with a Havok Behavior .hkx animation file
	"""

	__name__ = 'BSBehaviorGraphExtraData'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# Name of the hkx file.
		self.behaviour_graph_file = name_type_map['NiFixedString'](self.context, 0, None)

		# Unknown, has to do with blending appended bones onto an actor.
		self.controls_base_skeleton = name_type_map['Bool'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'behaviour_graph_file', name_type_map['NiFixedString'], (0, None), (False, None), (None, None)
		yield 'controls_base_skeleton', name_type_map['Bool'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'behaviour_graph_file', name_type_map['NiFixedString'], (0, None), (False, None)
		yield 'controls_base_skeleton', name_type_map['Bool'], (0, None), (False, None)
