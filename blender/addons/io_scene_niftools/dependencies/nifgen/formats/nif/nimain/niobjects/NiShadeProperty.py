from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiProperty import NiProperty


class NiShadeProperty(NiProperty):

	"""
	Determines whether flat shading or smooth shading is used on a shape.
	"""

	__name__ = 'NiShadeProperty'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.flags = name_type_map['ShadeFlags'].SHADING_SMOOTH
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'flags', name_type_map['ShadeFlags'], (0, None), (False, name_type_map['ShadeFlags'].SHADING_SMOOTH), (lambda context: context.bs_header.bs_version <= 34, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		if instance.context.bs_header.bs_version <= 34:
			yield 'flags', name_type_map['ShadeFlags'], (0, None), (False, name_type_map['ShadeFlags'].SHADING_SMOOTH)
