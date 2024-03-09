from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiNode import NiNode


class BSValueNode(NiNode):

	"""
	Bethesda-specific node. Found on fxFire effects
	"""

	__name__ = 'BSValueNode'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.value = name_type_map['Uint'](self.context, 0, None)
		self.value_node_flags = name_type_map['BSValueNodeFlags'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'value', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'value_node_flags', name_type_map['BSValueNodeFlags'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'value', name_type_map['Uint'], (0, None), (False, None)
		yield 'value_node_flags', name_type_map['BSValueNodeFlags'], (0, None), (False, None)
