from nifgen.formats.motiongraph.imports import name_type_map
from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct


class HeadTargetActivityData(MemStruct):

	"""
	? bytes
	"""

	__name__ = 'HeadTargetActivityData'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.weight = name_type_map['FloatInputData'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'weight', name_type_map['FloatInputData'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'weight', name_type_map['FloatInputData'], (0, None), (False, None)
