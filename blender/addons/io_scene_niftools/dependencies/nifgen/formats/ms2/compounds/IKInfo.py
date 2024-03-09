from nifgen.base_struct import BaseStruct
from nifgen.formats.ms2.compounds.BonePointer import BonePointer
import logging

from nifgen.array import Array
from nifgen.base_struct import BaseStruct
from nifgen.formats.ms2.imports import name_type_map


class IKInfo(BaseStruct):

	__name__ = 'IKInfo'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# needed for ZTUAC
		self.weird_padding = name_type_map['SmartPadding'](self.context, 0, None)

		# repeat
		self.ik_count = name_type_map['Uint64'](self.context, 0, None)
		self.ik_ptr = name_type_map['Uint64'](self.context, 0, None)

		# seen 0, 2, 4
		self.ik_targets_count = name_type_map['Uint64'](self.context, 0, None)
		self.ik_targets_ptr = name_type_map['Uint64'](self.context, 0, None)
		self.ik_ref = name_type_map['Empty'](self.context, 0, None)
		self.ik_list = Array(self.context, 0, None, (0,), name_type_map['IKEntry'])
		self.padding_0 = name_type_map['PadAlign'](self.context, 8, self.ik_ref)
		self.ik_targets = Array(self.context, 0, None, (0,), name_type_map['IKTarget'])
		self.padding_1 = name_type_map['PadAlign'](self.context, 8, self.ik_ref)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'weird_padding', name_type_map['SmartPadding'], (0, None), (False, None), (lambda context: context.version <= 13, None)
		yield 'ik_count', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'ik_ptr', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'ik_targets_count', name_type_map['Uint64'], (0, None), (False, None), (lambda context: context.version >= 48, None)
		yield 'ik_targets_ptr', name_type_map['Uint64'], (0, None), (False, None), (lambda context: context.version >= 48, None)
		yield 'ik_ref', name_type_map['Empty'], (0, None), (False, None), (None, None)
		yield 'ik_list', Array, (0, None, (None,), name_type_map['UACJoint']), (False, None), (lambda context: context.version <= 13, None)
		yield 'ik_list', Array, (0, None, (None,), name_type_map['IKEntry']), (False, None), (lambda context: context.version >= 32, None)
		yield 'padding_0', name_type_map['PadAlign'], (8, None), (False, None), (None, None)
		yield 'ik_targets', Array, (0, None, (None,), name_type_map['IKTarget']), (False, None), (lambda context: context.version >= 50, None)
		yield 'padding_1', name_type_map['PadAlign'], (8, None), (False, None), (lambda context: context.version >= 50, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		if instance.context.version <= 13:
			yield 'weird_padding', name_type_map['SmartPadding'], (0, None), (False, None)
		yield 'ik_count', name_type_map['Uint64'], (0, None), (False, None)
		yield 'ik_ptr', name_type_map['Uint64'], (0, None), (False, None)
		if instance.context.version >= 48:
			yield 'ik_targets_count', name_type_map['Uint64'], (0, None), (False, None)
			yield 'ik_targets_ptr', name_type_map['Uint64'], (0, None), (False, None)
		yield 'ik_ref', name_type_map['Empty'], (0, None), (False, None)
		if instance.context.version <= 13:
			yield 'ik_list', Array, (0, None, (instance.ik_count,), name_type_map['UACJoint']), (False, None)
		if instance.context.version >= 32:
			yield 'ik_list', Array, (0, None, (instance.ik_count,), name_type_map['IKEntry']), (False, None)
		yield 'padding_0', name_type_map['PadAlign'], (8, instance.ik_ref), (False, None)
		if instance.context.version >= 50:
			yield 'ik_targets', Array, (0, None, (instance.ik_targets_count,), name_type_map['IKTarget']), (False, None)
			yield 'padding_1', name_type_map['PadAlign'], (8, instance.ik_ref), (False, None)

	def get_pointers(self):
		"""Get all strings in the structure."""
		condition_function = lambda x: issubclass(x[1], BonePointer)
		for val in self.get_condition_values_recursive(self, condition_function):
			yield val

	@classmethod
	def read_fields(cls, stream, instance):
		super().read_fields(stream, instance)
		# after reading, we can resolve the bone pointers
		for ptr in instance.get_pointers():
			ptr.joint = instance.arg.bones[ptr.index]

	@classmethod
	def write_fields(cls, stream, instance):
		# update indices of bone pointers
		bones_map = {b: i for i, b in enumerate(instance.arg.bones)}
		for ptr in instance.get_pointers():
			ptr.index = bones_map.get(ptr.joint)
		super().write_fields(stream, instance)

