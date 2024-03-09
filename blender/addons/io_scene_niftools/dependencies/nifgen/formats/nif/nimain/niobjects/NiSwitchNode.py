from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiNode import NiNode


class NiSwitchNode(NiNode):

	"""
	Represents groups of multiple scenegraph subtrees, only one of which (the "active child") is drawn at any given time.
	"""

	__name__ = 'NiSwitchNode'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.switch_node_flags = name_type_map['NiSwitchFlags'].from_value(3)
		self.index = name_type_map['Uint'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'switch_node_flags', name_type_map['NiSwitchFlags'], (0, None), (False, 3), (lambda context: context.version >= 167837696, None)
		yield 'index', name_type_map['Uint'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		if instance.context.version >= 167837696:
			yield 'switch_node_flags', name_type_map['NiSwitchFlags'], (0, None), (False, 3)
		yield 'index', name_type_map['Uint'], (0, None), (False, None)
