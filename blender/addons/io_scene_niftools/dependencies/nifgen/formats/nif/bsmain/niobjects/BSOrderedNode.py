from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiNode import NiNode


class BSOrderedNode(NiNode):

	"""
	Bethesda-Specific node.
	"""

	__name__ = 'BSOrderedNode'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.alpha_sort_bound = name_type_map['Vector4'](self.context, 0, None)
		self.static_bound = name_type_map['Bool'].from_value(True)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'alpha_sort_bound', name_type_map['Vector4'], (0, None), (False, None), (None, None)
		yield 'static_bound', name_type_map['Bool'], (0, None), (False, True), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'alpha_sort_bound', name_type_map['Vector4'], (0, None), (False, None)
		yield 'static_bound', name_type_map['Bool'], (0, None), (False, True)
