from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiObject import NiObject


class NiTimeController(NiObject):

	"""
	Abstract base class that provides the base timing and update functionality for all the Gamebryo animation controllers.
	"""

	__name__ = 'NiTimeController'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# Index of the next controller.
		self.next_controller = name_type_map['Ref'](self.context, 0, name_type_map['NiTimeController'])
		self.flags = name_type_map['TimeControllerFlags'].from_value(76)

		# Frequency (is usually 1.0).
		self.frequency = name_type_map['Float'].from_value(1.0)

		# Phase (usually 0.0).
		self.phase = name_type_map['Float'](self.context, 0, None)

		# Controller start time.
		self.start_time = name_type_map['Float'].from_value(3.402823466e+38)

		# Controller stop time.
		self.stop_time = name_type_map['Float'].from_value(-3.402823466e+38)

		# Controller target (object index of the first controllable ancestor of this object).
		self.target = name_type_map['Ptr'](self.context, 0, name_type_map['NiObjectNET'])
		self.unknown_integer = name_type_map['Uint'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'next_controller', name_type_map['Ref'], (0, name_type_map['NiTimeController']), (False, None), (None, None)
		yield 'flags', name_type_map['TimeControllerFlags'], (0, None), (False, 76), (None, None)
		yield 'frequency', name_type_map['Float'], (0, None), (False, 1.0), (None, None)
		yield 'phase', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'start_time', name_type_map['Float'], (0, None), (False, 3.402823466e+38), (None, None)
		yield 'stop_time', name_type_map['Float'], (0, None), (False, -3.402823466e+38), (None, None)
		yield 'target', name_type_map['Ptr'], (0, name_type_map['NiObjectNET']), (False, None), (lambda context: context.version >= 50528269, None)
		yield 'unknown_integer', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.version <= 50397184, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'next_controller', name_type_map['Ref'], (0, name_type_map['NiTimeController']), (False, None)
		yield 'flags', name_type_map['TimeControllerFlags'], (0, None), (False, 76)
		yield 'frequency', name_type_map['Float'], (0, None), (False, 1.0)
		yield 'phase', name_type_map['Float'], (0, None), (False, None)
		yield 'start_time', name_type_map['Float'], (0, None), (False, 3.402823466e+38)
		yield 'stop_time', name_type_map['Float'], (0, None), (False, -3.402823466e+38)
		if instance.context.version >= 50528269:
			yield 'target', name_type_map['Ptr'], (0, name_type_map['NiObjectNET']), (False, None)
		if instance.context.version <= 50397184:
			yield 'unknown_integer', name_type_map['Uint'], (0, None), (False, None)
