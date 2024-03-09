from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiObject import NiObject


class NiEvaluator(NiObject):

	__name__ = 'NiEvaluator'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# The name of the animated NiAVObject.
		self.node_name = name_type_map['NiFixedString'](self.context, 0, None)

		# The RTTI type of the NiProperty the controller is attached to, if applicable.
		self.property_type = name_type_map['NiFixedString'](self.context, 0, None)

		# The RTTI type of the NiTimeController.
		self.controller_type = name_type_map['NiFixedString'](self.context, 0, None)

		# An ID that can uniquely identify the controller among others of the same type on the same NiObjectNET.
		self.controller_id = name_type_map['NiFixedString'](self.context, 0, None)

		# An ID that can uniquely identify the interpolator among others of the same type on the same NiObjectNET.
		self.interpolator_id = name_type_map['NiFixedString'](self.context, 0, None)

		# Channel Indices are BASE/POS = 0, ROT = 1, SCALE = 2, FLAG = 3
		# Channel Types are:
		# INVALID = 0, COLOR, BOOL, FLOAT, POINT3, ROT = 5
		# Any channel may be | 0x40 which means POSED
		# The FLAG (3) channel flags affects the whole evaluator:
		# REFERENCED = 0x1, TRANSFORM = 0x2, ALWAYSUPDATE = 0x4, SHUTDOWN = 0x8
		self.channel_types = Array(self.context, 0, None, (0,), name_type_map['Byte'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'node_name', name_type_map['NiFixedString'], (0, None), (False, None), (None, None)
		yield 'property_type', name_type_map['NiFixedString'], (0, None), (False, None), (None, None)
		yield 'controller_type', name_type_map['NiFixedString'], (0, None), (False, None), (None, None)
		yield 'controller_id', name_type_map['NiFixedString'], (0, None), (False, None), (None, None)
		yield 'interpolator_id', name_type_map['NiFixedString'], (0, None), (False, None), (None, None)
		yield 'channel_types', Array, (0, None, (4,), name_type_map['Byte']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'node_name', name_type_map['NiFixedString'], (0, None), (False, None)
		yield 'property_type', name_type_map['NiFixedString'], (0, None), (False, None)
		yield 'controller_type', name_type_map['NiFixedString'], (0, None), (False, None)
		yield 'controller_id', name_type_map['NiFixedString'], (0, None), (False, None)
		yield 'interpolator_id', name_type_map['NiFixedString'], (0, None), (False, None)
		yield 'channel_types', Array, (0, None, (4,), name_type_map['Byte']), (False, None)
