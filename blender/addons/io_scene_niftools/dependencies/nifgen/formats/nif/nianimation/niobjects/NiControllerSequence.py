import nifgen.formats.nif as NifFormat
from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nianimation.niobjects.NiSequence import NiSequence


class NiControllerSequence(NiSequence):

	"""
	Root node in Gamebryo .kf files (version 10.0.1.0 and up).
	"""

	__name__ = 'NiControllerSequence'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# The weight of a sequence describes how it blends with other sequences at the same priority.
		self.weight = name_type_map['Float'].from_value(1.0)
		self.text_keys = name_type_map['Ref'](self.context, 0, name_type_map['NiTextKeyExtraData'])
		self.cycle_type = name_type_map['CycleType'].CYCLE_CLAMP
		self.frequency = name_type_map['Float'].from_value(1.0)
		self.phase = name_type_map['Float'](self.context, 0, None)
		self.start_time = name_type_map['Float'].from_value(3.402823466e+38)
		self.stop_time = name_type_map['Float'].from_value(-3.402823466e+38)
		self.play_backwards = name_type_map['Bool'](self.context, 0, None)

		# The owner of this sequence.
		self.manager = name_type_map['Ptr'](self.context, 0, name_type_map['NiControllerManager'])

		# The name of the NiAVObject serving as the accumulation root. This is where all accumulated translations, scales, and rotations are applied.
		self.accum_root_name = name_type_map['String'](self.context, 0, None)
		self.accum_flags = name_type_map['AccumFlags'].from_value(64)
		self.string_palette = name_type_map['Ref'](self.context, 0, name_type_map['NiStringPalette'])
		self.anim_notes = name_type_map['Ref'](self.context, 0, name_type_map['BSAnimNotes'])
		self.num_anim_note_arrays = name_type_map['Ushort'](self.context, 0, None)
		self.anim_note_arrays = Array(self.context, 0, name_type_map['BSAnimNotes'], (0,), name_type_map['Ref'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'weight', name_type_map['Float'], (0, None), (False, 1.0), (lambda context: context.version >= 167837802, None)
		yield 'text_keys', name_type_map['Ref'], (0, name_type_map['NiTextKeyExtraData']), (False, None), (lambda context: context.version >= 167837802, None)
		yield 'cycle_type', name_type_map['CycleType'], (0, None), (False, name_type_map['CycleType'].CYCLE_CLAMP), (lambda context: context.version >= 167837802, None)
		yield 'frequency', name_type_map['Float'], (0, None), (False, 1.0), (lambda context: context.version >= 167837802, None)
		yield 'phase', name_type_map['Float'], (0, None), (False, None), (lambda context: 167837802 <= context.version <= 168034305, None)
		yield 'start_time', name_type_map['Float'], (0, None), (False, 3.402823466e+38), (lambda context: context.version >= 167837802, None)
		yield 'stop_time', name_type_map['Float'], (0, None), (False, -3.402823466e+38), (lambda context: context.version >= 167837802, None)
		yield 'play_backwards', name_type_map['Bool'], (0, None), (False, None), (lambda context: 167837802 <= context.version <= 167837802, None)
		yield 'manager', name_type_map['Ptr'], (0, name_type_map['NiControllerManager']), (False, None), (lambda context: context.version >= 167837802, None)
		yield 'accum_root_name', name_type_map['String'], (0, None), (False, None), (lambda context: context.version >= 167837802, None)
		yield 'accum_flags', name_type_map['AccumFlags'], (0, None), (False, 64), (lambda context: context.version >= 335740936, None)
		yield 'string_palette', name_type_map['Ref'], (0, name_type_map['NiStringPalette']), (False, None), (lambda context: 167837809 <= context.version <= 335609856, None)
		yield 'anim_notes', name_type_map['Ref'], (0, name_type_map['BSAnimNotes']), (False, None), (lambda context: context.version >= 335675399 and (context.bs_header.bs_version >= 24) and (context.bs_header.bs_version <= 28), None)
		yield 'num_anim_note_arrays', name_type_map['Ushort'], (0, None), (False, None), (lambda context: context.version >= 335675399 and context.bs_header.bs_version > 28, None)
		yield 'anim_note_arrays', Array, (0, name_type_map['BSAnimNotes'], (None,), name_type_map['Ref']), (False, None), (lambda context: context.version >= 335675399 and context.bs_header.bs_version > 28, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		if instance.context.version >= 167837802:
			yield 'weight', name_type_map['Float'], (0, None), (False, 1.0)
			yield 'text_keys', name_type_map['Ref'], (0, name_type_map['NiTextKeyExtraData']), (False, None)
			yield 'cycle_type', name_type_map['CycleType'], (0, None), (False, name_type_map['CycleType'].CYCLE_CLAMP)
			yield 'frequency', name_type_map['Float'], (0, None), (False, 1.0)
		if 167837802 <= instance.context.version <= 168034305:
			yield 'phase', name_type_map['Float'], (0, None), (False, None)
		if instance.context.version >= 167837802:
			yield 'start_time', name_type_map['Float'], (0, None), (False, 3.402823466e+38)
			yield 'stop_time', name_type_map['Float'], (0, None), (False, -3.402823466e+38)
		if 167837802 <= instance.context.version <= 167837802:
			yield 'play_backwards', name_type_map['Bool'], (0, None), (False, None)
		if instance.context.version >= 167837802:
			yield 'manager', name_type_map['Ptr'], (0, name_type_map['NiControllerManager']), (False, None)
			yield 'accum_root_name', name_type_map['String'], (0, None), (False, None)
		if instance.context.version >= 335740936:
			yield 'accum_flags', name_type_map['AccumFlags'], (0, None), (False, 64)
		if 167837809 <= instance.context.version <= 335609856:
			yield 'string_palette', name_type_map['Ref'], (0, name_type_map['NiStringPalette']), (False, None)
		if instance.context.version >= 335675399 and (instance.context.bs_header.bs_version >= 24) and (instance.context.bs_header.bs_version <= 28):
			yield 'anim_notes', name_type_map['Ref'], (0, name_type_map['BSAnimNotes']), (False, None)
		if instance.context.version >= 335675399 and instance.context.bs_header.bs_version > 28:
			yield 'num_anim_note_arrays', name_type_map['Ushort'], (0, None), (False, None)
			yield 'anim_note_arrays', Array, (0, name_type_map['BSAnimNotes'], (instance.num_anim_note_arrays,), name_type_map['Ref']), (False, None)
	def add_controlled_block(self):
		"""Create new controlled block, and return it.

		>>> seq = NifFormat.NiControllerSequence()
		>>> seq.num_controlled_blocks
		0
		>>> ctrlblock = seq.add_controlled_block()
		>>> seq.num_controlled_blocks
		1
		>>> isinstance(ctrlblock, NifFormat.ControllerLink)
		True
		"""
		# add to the list
		num_blocks = self.num_controlled_blocks
		self.num_controlled_blocks = num_blocks + 1
		self.controlled_blocks.append(NifFormat.classes.ControlledBlock(self.context))
		self.controlled_blocks.shape = (self.num_controlled_blocks, *self.controlled_blocks.shape[1:])
		return self.controlled_blocks[-1]

