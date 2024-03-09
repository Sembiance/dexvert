from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiObject import NiObject


class NiSequenceData(NiObject):

	"""
	Root node in Gamebryo .kf files (20.5.0.1 and up).
	For 20.5.0.0, "NiSequenceData" is an alias for "NiControllerSequence" and this is not handled in nifxml.
	This was not found in any 20.5.0.0 KFs available and they instead use NiControllerSequence directly.
	After 20.5.0.1, Controlled Blocks are no longer used and instead the sequences uses NiEvaluator.
	"""

	__name__ = 'NiSequenceData'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.name = name_type_map['NiFixedString'](self.context, 0, None)
		self.num_controlled_blocks = name_type_map['Uint'](self.context, 0, None)
		self.array_grow_by = name_type_map['Uint'](self.context, 0, None)
		self.controlled_blocks = Array(self.context, 0, None, (0,), name_type_map['ControlledBlock'])
		self.num_evaluators = name_type_map['Uint'](self.context, 0, None)
		self.evaluators = Array(self.context, 0, name_type_map['NiEvaluator'], (0,), name_type_map['Ref'])
		self.text_keys = name_type_map['Ref'](self.context, 0, name_type_map['NiTextKeyExtraData'])
		self.duration = name_type_map['Float'](self.context, 0, None)
		self.cycle_type = name_type_map['CycleType'](self.context, 0, None)
		self.frequency = name_type_map['Float'].from_value(1.0)

		# The name of the NiAVObject serving as the accumulation root. This is where all accumulated translations, scales, and rotations are applied.
		self.accum_root_name = name_type_map['NiFixedString'](self.context, 0, None)
		self.accum_flags = name_type_map['AccumFlags'].from_value(64)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'name', name_type_map['NiFixedString'], (0, None), (False, None), (None, None)
		yield 'num_controlled_blocks', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.version <= 335872001, None)
		yield 'array_grow_by', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.version <= 335872001, None)
		yield 'controlled_blocks', Array, (0, None, (None,), name_type_map['ControlledBlock']), (False, None), (lambda context: context.version <= 335872001, None)
		yield 'num_evaluators', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.version >= 335872002, None)
		yield 'evaluators', Array, (0, name_type_map['NiEvaluator'], (None,), name_type_map['Ref']), (False, None), (lambda context: context.version >= 335872002, None)
		yield 'text_keys', name_type_map['Ref'], (0, name_type_map['NiTextKeyExtraData']), (False, None), (None, None)
		yield 'duration', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'cycle_type', name_type_map['CycleType'], (0, None), (False, None), (None, None)
		yield 'frequency', name_type_map['Float'], (0, None), (False, 1.0), (None, None)
		yield 'accum_root_name', name_type_map['NiFixedString'], (0, None), (False, None), (None, None)
		yield 'accum_flags', name_type_map['AccumFlags'], (0, None), (False, 64), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'name', name_type_map['NiFixedString'], (0, None), (False, None)
		if instance.context.version <= 335872001:
			yield 'num_controlled_blocks', name_type_map['Uint'], (0, None), (False, None)
			yield 'array_grow_by', name_type_map['Uint'], (0, None), (False, None)
			yield 'controlled_blocks', Array, (0, None, (instance.num_controlled_blocks,), name_type_map['ControlledBlock']), (False, None)
		if instance.context.version >= 335872002:
			yield 'num_evaluators', name_type_map['Uint'], (0, None), (False, None)
			yield 'evaluators', Array, (0, name_type_map['NiEvaluator'], (instance.num_evaluators,), name_type_map['Ref']), (False, None)
		yield 'text_keys', name_type_map['Ref'], (0, name_type_map['NiTextKeyExtraData']), (False, None)
		yield 'duration', name_type_map['Float'], (0, None), (False, None)
		yield 'cycle_type', name_type_map['CycleType'], (0, None), (False, None)
		yield 'frequency', name_type_map['Float'], (0, None), (False, 1.0)
		yield 'accum_root_name', name_type_map['NiFixedString'], (0, None), (False, None)
		yield 'accum_flags', name_type_map['AccumFlags'], (0, None), (False, 64)
