from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiNode import NiNode


class BSTreeNode(NiNode):

	"""
	Node for handling Trees, Switches branch configurations for variation?
	"""

	__name__ = 'BSTreeNode'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.num_bones_1 = name_type_map['Uint'].from_value(1)
		self.bones_1 = Array(self.context, 0, name_type_map['NiNode'], (0,), name_type_map['Ref'])
		self.num_bones_2 = name_type_map['Uint'].from_value(3)
		self.bones = Array(self.context, 0, name_type_map['NiNode'], (0,), name_type_map['Ref'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'num_bones_1', name_type_map['Uint'], (0, None), (False, 1), (None, None)
		yield 'bones_1', Array, (0, name_type_map['NiNode'], (None,), name_type_map['Ref']), (False, None), (None, None)
		yield 'num_bones_2', name_type_map['Uint'], (0, None), (False, 3), (None, None)
		yield 'bones', Array, (0, name_type_map['NiNode'], (None,), name_type_map['Ref']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'num_bones_1', name_type_map['Uint'], (0, None), (False, 1)
		yield 'bones_1', Array, (0, name_type_map['NiNode'], (instance.num_bones_1,), name_type_map['Ref']), (False, None)
		yield 'num_bones_2', name_type_map['Uint'], (0, None), (False, 3)
		yield 'bones', Array, (0, name_type_map['NiNode'], (instance.num_bones_2,), name_type_map['Ref']), (False, None)
