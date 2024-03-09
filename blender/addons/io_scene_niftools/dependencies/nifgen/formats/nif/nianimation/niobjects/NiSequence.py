from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiObject import NiObject


class NiSequence(NiObject):

	"""
	Root node in NetImmerse .kf files (until version 10.0).
	"""

	__name__ = 'NiSequence'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# The sequence name by which the animation system finds and manages this sequence.
		self.name = name_type_map['String'](self.context, 0, None)

		# The name of the NiAVObject serving as the accumulation root. This is where all accumulated translations, scales, and rotations are applied.
		self.accum_root_name = name_type_map['String'](self.context, 0, None)
		self.text_keys = name_type_map['Ref'](self.context, 0, name_type_map['NiTextKeyExtraData'])
		self.num_div_2_ints = name_type_map['Uint'](self.context, 0, None)
		self.div_2_ints = Array(self.context, 0, None, (0,), name_type_map['Int'])
		self.div_2_ref = name_type_map['Ref'](self.context, 0, name_type_map['NiObject'])
		self.num_controlled_blocks = name_type_map['Uint'](self.context, 0, None)
		self.array_grow_by = name_type_map['Uint'].from_value(1)
		self.controlled_blocks = Array(self.context, 0, None, (0,), name_type_map['ControlledBlock'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'name', name_type_map['String'], (0, None), (False, None), (None, None)
		yield 'accum_root_name', name_type_map['String'], (0, None), (False, None), (lambda context: context.version <= 167837799, None)
		yield 'text_keys', name_type_map['Ref'], (0, name_type_map['NiTextKeyExtraData']), (False, None), (lambda context: context.version <= 167837799, None)
		yield 'num_div_2_ints', name_type_map['Uint'], (0, None), (False, None), (lambda context: 335740937 <= context.version <= 335740937 and (context.user_version == 131072) or (context.user_version == 196608), None)
		yield 'div_2_ints', Array, (0, None, (None,), name_type_map['Int']), (False, None), (lambda context: 335740937 <= context.version <= 335740937 and (context.user_version == 131072) or (context.user_version == 196608), None)
		yield 'div_2_ref', name_type_map['Ref'], (0, name_type_map['NiObject']), (False, None), (lambda context: 335740937 <= context.version <= 335740937 and (context.user_version == 131072) or (context.user_version == 196608), None)
		yield 'num_controlled_blocks', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'array_grow_by', name_type_map['Uint'], (0, None), (False, 1), (lambda context: context.version >= 167837802, None)
		yield 'controlled_blocks', Array, (0, None, (None,), name_type_map['ControlledBlock']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'name', name_type_map['String'], (0, None), (False, None)
		if instance.context.version <= 167837799:
			yield 'accum_root_name', name_type_map['String'], (0, None), (False, None)
			yield 'text_keys', name_type_map['Ref'], (0, name_type_map['NiTextKeyExtraData']), (False, None)
		if 335740937 <= instance.context.version <= 335740937 and (instance.context.user_version == 131072) or (instance.context.user_version == 196608):
			yield 'num_div_2_ints', name_type_map['Uint'], (0, None), (False, None)
			yield 'div_2_ints', Array, (0, None, (instance.num_div_2_ints,), name_type_map['Int']), (False, None)
			yield 'div_2_ref', name_type_map['Ref'], (0, name_type_map['NiObject']), (False, None)
		yield 'num_controlled_blocks', name_type_map['Uint'], (0, None), (False, None)
		if instance.context.version >= 167837802:
			yield 'array_grow_by', name_type_map['Uint'], (0, None), (False, 1)
		yield 'controlled_blocks', Array, (0, None, (instance.num_controlled_blocks,), name_type_map['ControlledBlock']), (False, None)
