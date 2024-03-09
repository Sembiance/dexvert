from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiNode import NiNode


class BSMultiBoundNode(NiNode):

	"""
	Bethesda-specific node.
	"""

	__name__ = 'BSMultiBoundNode'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.multi_bound = name_type_map['Ref'](self.context, 0, name_type_map['BSMultiBound'])
		self.culling_mode = name_type_map['BSCPCullingType'].CULL_ALLPASS
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'multi_bound', name_type_map['Ref'], (0, name_type_map['BSMultiBound']), (False, None), (None, None)
		yield 'culling_mode', name_type_map['BSCPCullingType'], (0, None), (False, name_type_map['BSCPCullingType'].CULL_ALLPASS), (lambda context: context.bs_header.bs_version >= 83, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'multi_bound', name_type_map['Ref'], (0, name_type_map['BSMultiBound']), (False, None)
		if instance.context.bs_header.bs_version >= 83:
			yield 'culling_mode', name_type_map['BSCPCullingType'], (0, None), (False, name_type_map['BSCPCullingType'].CULL_ALLPASS)
