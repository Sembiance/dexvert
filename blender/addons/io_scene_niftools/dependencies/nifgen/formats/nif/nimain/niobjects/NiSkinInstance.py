from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiObject import NiObject


class NiSkinInstance(NiObject):

	"""
	Skinning instance.
	"""

	__name__ = 'NiSkinInstance'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# Skinning data reference.
		self.data = name_type_map['Ref'](self.context, 0, name_type_map['NiSkinData'])

		# Refers to a NiSkinPartition objects, which partitions the mesh such that every vertex is only influenced by a limited number of bones.
		self.skin_partition = name_type_map['Ref'](self.context, 0, name_type_map['NiSkinPartition'])

		# Armature root node.
		self.skeleton_root = name_type_map['Ptr'](self.context, 0, name_type_map['NiNode'])

		# The number of node bones referenced as influences.
		self.num_bones = name_type_map['Uint'](self.context, 0, None)

		# List of all armature bones.
		self.bones = Array(self.context, 0, name_type_map['NiNode'], (0,), name_type_map['Ptr'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'data', name_type_map['Ref'], (0, name_type_map['NiSkinData']), (False, None), (None, None)
		yield 'skin_partition', name_type_map['Ref'], (0, name_type_map['NiSkinPartition']), (False, None), (lambda context: context.version >= 167837797, None)
		yield 'skeleton_root', name_type_map['Ptr'], (0, name_type_map['NiNode']), (False, None), (None, None)
		yield 'num_bones', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'bones', Array, (0, name_type_map['NiNode'], (None,), name_type_map['Ptr']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'data', name_type_map['Ref'], (0, name_type_map['NiSkinData']), (False, None)
		if instance.context.version >= 167837797:
			yield 'skin_partition', name_type_map['Ref'], (0, name_type_map['NiSkinPartition']), (False, None)
		yield 'skeleton_root', name_type_map['Ptr'], (0, name_type_map['NiNode']), (False, None)
		yield 'num_bones', name_type_map['Uint'], (0, None), (False, None)
		yield 'bones', Array, (0, name_type_map['NiNode'], (instance.num_bones,), name_type_map['Ptr']), (False, None)
