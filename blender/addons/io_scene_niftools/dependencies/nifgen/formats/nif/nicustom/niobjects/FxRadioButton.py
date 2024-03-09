from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nicustom.niobjects.FxWidget import FxWidget


class FxRadioButton(FxWidget):

	"""
	Unknown.
	"""

	__name__ = 'FxRadioButton'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.unknown_int_1 = name_type_map['Uint'](self.context, 0, None)
		self.unknown_int_2 = name_type_map['Uint'](self.context, 0, None)
		self.unknown_int_3 = name_type_map['Uint'](self.context, 0, None)

		# Number of unknown links.
		self.num_buttons = name_type_map['Uint'](self.context, 0, None)

		# Unknown pointers to other buttons.  Maybe other buttons in a group so they can be switch off if this one is switched on?
		self.buttons = Array(self.context, 0, name_type_map['FxRadioButton'], (0,), name_type_map['Ptr'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'unknown_int_1', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'unknown_int_2', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'unknown_int_3', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'num_buttons', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'buttons', Array, (0, name_type_map['FxRadioButton'], (None,), name_type_map['Ptr']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'unknown_int_1', name_type_map['Uint'], (0, None), (False, None)
		yield 'unknown_int_2', name_type_map['Uint'], (0, None), (False, None)
		yield 'unknown_int_3', name_type_map['Uint'], (0, None), (False, None)
		yield 'num_buttons', name_type_map['Uint'], (0, None), (False, None)
		yield 'buttons', Array, (0, name_type_map['FxRadioButton'], (instance.num_buttons,), name_type_map['Ptr']), (False, None)
