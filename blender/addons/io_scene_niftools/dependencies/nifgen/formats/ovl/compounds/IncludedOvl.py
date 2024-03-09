from nifgen.base_struct import BaseStruct
from nifgen.formats.ovl.imports import name_type_map


class IncludedOvl(BaseStruct):

	"""
	Description of one included ovl file that is force-loaded by this ovl
	"""

	__name__ = 'IncludedOvl'

	allow_np = True

	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# path is relative to this ovl's directory; usually points to ovl files
		self.basename = name_type_map['OffsetString'](self.context, self.context.names, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'basename', name_type_map['OffsetString'], (None, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'basename', name_type_map['OffsetString'], (instance.context.names, None), (False, None)
