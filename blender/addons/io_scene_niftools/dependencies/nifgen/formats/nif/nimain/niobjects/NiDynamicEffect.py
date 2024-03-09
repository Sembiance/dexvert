from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiAVObject import NiAVObject


class NiDynamicEffect(NiAVObject):

	"""
	Abstract base class for dynamic effects such as NiLights or projected texture effects.
	"""

	__name__ = 'NiDynamicEffect'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# If true, then the dynamic effect is applied to affected nodes during rendering.
		self.switch_state = name_type_map['Bool'].from_value(True)
		self.num_affected_nodes = name_type_map['Uint'](self.context, 0, None)

		# If a node appears in this list, then its entire subtree will be affected by the effect.
		self.affected_nodes = Array(self.context, 0, name_type_map['NiNode'], (0,), name_type_map['Ptr'])

		# As of 4.0 the pointer hash is no longer stored alongside each NiObject on disk, yet this node list still refers to the pointer hashes. Cannot leave the type as Ptr because the link will be invalid.
		self.affected_node_pointers = Array(self.context, 0, None, (0,), name_type_map['Uint'])
		self.num_affected_nodes = name_type_map['Uint'](self.context, 0, None)

		# If a node appears in this list, then its entire subtree will be affected by the effect.
		self.affected_nodes = Array(self.context, 0, name_type_map['NiNode'], (0,), name_type_map['Ptr'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'switch_state', name_type_map['Bool'], (0, None), (False, True), (lambda context: context.version >= 167837802 and context.bs_header.bs_version < 130, None)
		yield 'num_affected_nodes', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.version <= 67108866, None)
		yield 'affected_nodes', Array, (0, name_type_map['NiNode'], (None,), name_type_map['Ptr']), (False, None), (lambda context: context.version <= 50528269, None)
		yield 'affected_node_pointers', Array, (0, None, (None,), name_type_map['Uint']), (False, None), (lambda context: 67108864 <= context.version <= 67108866, None)
		yield 'num_affected_nodes', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.version >= 167837696 and context.bs_header.bs_version < 130, None)
		yield 'affected_nodes', Array, (0, name_type_map['NiNode'], (None,), name_type_map['Ptr']), (False, None), (lambda context: context.version >= 167837696 and context.bs_header.bs_version < 130, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		if instance.context.version >= 167837802 and instance.context.bs_header.bs_version < 130:
			yield 'switch_state', name_type_map['Bool'], (0, None), (False, True)
		if instance.context.version <= 67108866:
			yield 'num_affected_nodes', name_type_map['Uint'], (0, None), (False, None)
		if instance.context.version <= 50528269:
			yield 'affected_nodes', Array, (0, name_type_map['NiNode'], (instance.num_affected_nodes,), name_type_map['Ptr']), (False, None)
		if 67108864 <= instance.context.version <= 67108866:
			yield 'affected_node_pointers', Array, (0, None, (instance.num_affected_nodes,), name_type_map['Uint']), (False, None)
		if instance.context.version >= 167837696 and instance.context.bs_header.bs_version < 130:
			yield 'num_affected_nodes', name_type_map['Uint'], (0, None), (False, None)
			yield 'affected_nodes', Array, (0, name_type_map['NiNode'], (instance.num_affected_nodes,), name_type_map['Ptr']), (False, None)
