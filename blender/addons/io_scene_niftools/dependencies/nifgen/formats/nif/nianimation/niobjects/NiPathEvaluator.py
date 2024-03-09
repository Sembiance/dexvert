from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nianimation.niobjects.NiKeyBasedEvaluator import NiKeyBasedEvaluator


class NiPathEvaluator(NiKeyBasedEvaluator):

	__name__ = 'NiPathEvaluator'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.flags = name_type_map['PathFlags'].from_value(3)

		# -1 = Negative, 1 = Positive
		self.bank_dir = name_type_map['Int'].from_value(1)

		# Max angle in radians.
		self.max_bank_angle = name_type_map['Float'](self.context, 0, None)
		self.smoothing = name_type_map['Float'](self.context, 0, None)

		# 0, 1, or 2 representing X, Y, or Z.
		self.follow_axis = name_type_map['Short'](self.context, 0, None)
		self.path_data = name_type_map['Ref'](self.context, 0, name_type_map['NiPosData'])
		self.percent_data = name_type_map['Ref'](self.context, 0, name_type_map['NiFloatData'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'flags', name_type_map['PathFlags'], (0, None), (False, 3), (None, None)
		yield 'bank_dir', name_type_map['Int'], (0, None), (False, 1), (None, None)
		yield 'max_bank_angle', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'smoothing', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'follow_axis', name_type_map['Short'], (0, None), (False, None), (None, None)
		yield 'path_data', name_type_map['Ref'], (0, name_type_map['NiPosData']), (False, None), (None, None)
		yield 'percent_data', name_type_map['Ref'], (0, name_type_map['NiFloatData']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'flags', name_type_map['PathFlags'], (0, None), (False, 3)
		yield 'bank_dir', name_type_map['Int'], (0, None), (False, 1)
		yield 'max_bank_angle', name_type_map['Float'], (0, None), (False, None)
		yield 'smoothing', name_type_map['Float'], (0, None), (False, None)
		yield 'follow_axis', name_type_map['Short'], (0, None), (False, None)
		yield 'path_data', name_type_map['Ref'], (0, name_type_map['NiPosData']), (False, None)
		yield 'percent_data', name_type_map['Ref'], (0, name_type_map['NiFloatData']), (False, None)
