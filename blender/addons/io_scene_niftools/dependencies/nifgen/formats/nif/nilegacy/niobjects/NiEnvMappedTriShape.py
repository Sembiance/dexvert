from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiObjectNET import NiObjectNET


class NiEnvMappedTriShape(NiObjectNET):

	"""
	Unknown
	"""

	__name__ = 'NiEnvMappedTriShape'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.unknown_1 = name_type_map['Ushort'](self.context, 0, None)
		self.unknown_matrix = name_type_map['Matrix44'](self.context, 0, None)

		# The number of child objects.
		self.num_children = name_type_map['Uint'](self.context, 0, None)

		# List of child node object indices.
		self.children = Array(self.context, 0, name_type_map['NiAVObject'], (0,), name_type_map['Ref'])
		self.child_2 = name_type_map['Ref'](self.context, 0, name_type_map['NiObject'])
		self.child_3 = name_type_map['Ref'](self.context, 0, name_type_map['NiObject'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'unknown_1', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'unknown_matrix', name_type_map['Matrix44'], (0, None), (False, None), (None, None)
		yield 'num_children', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'children', Array, (0, name_type_map['NiAVObject'], (None,), name_type_map['Ref']), (False, None), (None, None)
		yield 'child_2', name_type_map['Ref'], (0, name_type_map['NiObject']), (False, None), (None, None)
		yield 'child_3', name_type_map['Ref'], (0, name_type_map['NiObject']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'unknown_1', name_type_map['Ushort'], (0, None), (False, None)
		yield 'unknown_matrix', name_type_map['Matrix44'], (0, None), (False, None)
		yield 'num_children', name_type_map['Uint'], (0, None), (False, None)
		yield 'children', Array, (0, name_type_map['NiAVObject'], (instance.num_children,), name_type_map['Ref']), (False, None)
		yield 'child_2', name_type_map['Ref'], (0, name_type_map['NiObject']), (False, None)
		yield 'child_3', name_type_map['Ref'], (0, name_type_map['NiObject']), (False, None)
