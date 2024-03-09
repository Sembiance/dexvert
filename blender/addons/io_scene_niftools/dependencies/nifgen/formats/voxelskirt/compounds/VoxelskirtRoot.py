from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct
from nifgen.formats.voxelskirt.imports import name_type_map


class VoxelskirtRoot(MemStruct):

	"""
	# size varies according to game
	JWE2 - 120 bytes
	"""

	__name__ = 'VoxelskirtRoot'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.zero = name_type_map['Uint64'].from_value(0)

		# total size of buffer data
		self._data_size = name_type_map['Uint64'](self.context, 0, None)
		self.x = name_type_map['Uint64'](self.context, 0, None)
		self.y = name_type_map['Uint64'](self.context, 0, None)

		# multiply by x or y to get the actual dimension of skirt, eg 512px * 16.0 = 8192.0m
		self.scale = name_type_map['Float'](self.context, 0, None)
		self.padding = name_type_map['Uint'].from_value(0)

		# zero, for PC only
		self._height_offset = name_type_map['Uint64'](self.context, 0, None)

		# x*y*4, for PC only
		self._weights_offset = name_type_map['Uint64'](self.context, 0, None)
		self.layers = name_type_map['DataSlot'](self.context, 0, name_type_map['Layer'])
		self.areas = name_type_map['DataSlot'](self.context, 0, name_type_map['Area'])
		self.entity_groups = name_type_map['DataSlot'](self.context, 0, name_type_map['EntityGroup'])
		self.materials = name_type_map['DataSlot'](self.context, 0, name_type_map['Material'])
		self.names = name_type_map['DataSlot'](self.context, 0, name_type_map['Name'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'zero', name_type_map['Uint64'], (0, None), (True, 0), (None, None)
		yield '_data_size', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'x', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'y', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'scale', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'padding', name_type_map['Uint'], (0, None), (True, 0), (None, None)
		yield '_height_offset', name_type_map['Uint64'], (0, None), (False, None), (lambda context: context.version == 18, None)
		yield '_weights_offset', name_type_map['Uint64'], (0, None), (False, None), (lambda context: context.version == 18, None)
		yield 'layers', name_type_map['DataSlot'], (0, name_type_map['Layer']), (False, None), (lambda context: not (context.version == 18), None)
		yield 'areas', name_type_map['DataSlot'], (0, name_type_map['Area']), (False, None), (lambda context: not (context.version == 18), None)
		yield 'entity_groups', name_type_map['DataSlot'], (0, name_type_map['EntityGroup']), (False, None), (None, None)
		yield 'materials', name_type_map['DataSlot'], (0, name_type_map['Material']), (False, None), (None, None)
		yield 'names', name_type_map['DataSlot'], (0, name_type_map['Name']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'zero', name_type_map['Uint64'], (0, None), (True, 0)
		yield '_data_size', name_type_map['Uint64'], (0, None), (False, None)
		yield 'x', name_type_map['Uint64'], (0, None), (False, None)
		yield 'y', name_type_map['Uint64'], (0, None), (False, None)
		yield 'scale', name_type_map['Float'], (0, None), (False, None)
		yield 'padding', name_type_map['Uint'], (0, None), (True, 0)
		if instance.context.version == 18:
			yield '_height_offset', name_type_map['Uint64'], (0, None), (False, None)
			yield '_weights_offset', name_type_map['Uint64'], (0, None), (False, None)
		if not (instance.context.version == 18):
			yield 'layers', name_type_map['DataSlot'], (0, name_type_map['Layer']), (False, None)
			yield 'areas', name_type_map['DataSlot'], (0, name_type_map['Area']), (False, None)
		yield 'entity_groups', name_type_map['DataSlot'], (0, name_type_map['EntityGroup']), (False, None)
		yield 'materials', name_type_map['DataSlot'], (0, name_type_map['Material']), (False, None)
		yield 'names', name_type_map['DataSlot'], (0, name_type_map['Name']), (False, None)
