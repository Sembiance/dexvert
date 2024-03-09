from nifgen.formats.habitatboundary.imports import name_type_map
from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct


class HbPostSize(MemStruct):

	__name__ = 'HB_PostSize'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# Post size front and back. Affects navcut and selection.
		self.front_back = name_type_map['Float'](self.context, 0, None)

		# Post size left and right. Affects navcut and selection.
		self.left_right = name_type_map['Float'](self.context, 0, None)

		# Post size above wall. Affects navcut and selection.
		self.top = name_type_map['Float'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'front_back', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'left_right', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'top', name_type_map['Float'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'front_back', name_type_map['Float'], (0, None), (False, None)
		yield 'left_right', name_type_map['Float'], (0, None), (False, None)
		yield 'top', name_type_map['Float'], (0, None), (False, None)
