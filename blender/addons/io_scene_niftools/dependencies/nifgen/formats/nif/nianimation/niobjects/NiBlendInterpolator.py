from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nianimation.niobjects.NiInterpolator import NiInterpolator


class NiBlendInterpolator(NiInterpolator):

	"""
	Abstract base class for all NiInterpolators that blend the results of sub-interpolators together to compute a final weighted value.
	"""

	__name__ = 'NiBlendInterpolator'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.flags = name_type_map['InterpBlendFlags'](self.context, 0, None)
		self.array_size = name_type_map['Ushort'](self.context, 0, None)
		self.array_grow_by = name_type_map['Ushort'](self.context, 0, None)
		self.array_size = name_type_map['Byte'](self.context, 0, None)
		self.weight_threshold = name_type_map['Float'](self.context, 0, None)
		self.interp_count = name_type_map['Byte'](self.context, 0, None)
		self.single_index = name_type_map['Byte'].from_value(255)
		self.high_priority = name_type_map['Sbyte'].from_value(-128)
		self.next_high_priority = name_type_map['Sbyte'].from_value(-128)
		self.single_time = name_type_map['Float'].from_value(-3.402823466e+38)
		self.high_weights_sum = name_type_map['Float'].from_value(-3.402823466e+38)
		self.next_high_weights_sum = name_type_map['Float'].from_value(-3.402823466e+38)
		self.high_ease_spinner = name_type_map['Float'].from_value(-3.402823466e+38)
		self.interp_array_items = Array(self.context, 0, None, (0,), name_type_map['InterpBlendItem'])
		self.manager_controlled = name_type_map['Bool'](self.context, 0, None)
		self.weight_threshold = name_type_map['Float'](self.context, 0, None)
		self.only_use_highest_weight = name_type_map['Bool'](self.context, 0, None)
		self.interp_count = name_type_map['Ushort'](self.context, 0, None)
		self.single_index = name_type_map['Ushort'].from_value(65535)
		self.interp_count = name_type_map['Byte'](self.context, 0, None)
		self.single_index = name_type_map['Byte'].from_value(255)
		self.single_interpolator = name_type_map['Ref'](self.context, 0, name_type_map['NiInterpolator'])
		self.single_time = name_type_map['Float'].from_value(-3.402823466e+38)
		self.high_priority = name_type_map['Int'].from_value(-2147483648)
		self.next_high_priority = name_type_map['Int'].from_value(-2147483648)
		self.high_priority = name_type_map['Sbyte'].from_value(-128)
		self.next_high_priority = name_type_map['Sbyte'].from_value(-128)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'flags', name_type_map['InterpBlendFlags'], (0, None), (False, None), (lambda context: context.version >= 167837808, None)
		yield 'array_size', name_type_map['Ushort'], (0, None), (False, None), (lambda context: context.version <= 167837805, None)
		yield 'array_grow_by', name_type_map['Ushort'], (0, None), (False, None), (lambda context: context.version <= 167837805, None)
		yield 'array_size', name_type_map['Byte'], (0, None), (False, None), (lambda context: context.version >= 167837806, None)
		yield 'weight_threshold', name_type_map['Float'], (0, None), (False, None), (lambda context: context.version >= 167837808, None)
		yield 'interp_count', name_type_map['Byte'], (0, None), (False, None), (lambda context: context.version >= 167837808, True)
		yield 'single_index', name_type_map['Byte'], (0, None), (False, 255), (lambda context: context.version >= 167837808, True)
		yield 'high_priority', name_type_map['Sbyte'], (0, None), (False, -128), (lambda context: context.version >= 167837808, True)
		yield 'next_high_priority', name_type_map['Sbyte'], (0, None), (False, -128), (lambda context: context.version >= 167837808, True)
		yield 'single_time', name_type_map['Float'], (0, None), (False, -3.402823466e+38), (lambda context: context.version >= 167837808, True)
		yield 'high_weights_sum', name_type_map['Float'], (0, None), (False, -3.402823466e+38), (lambda context: context.version >= 167837808, True)
		yield 'next_high_weights_sum', name_type_map['Float'], (0, None), (False, -3.402823466e+38), (lambda context: context.version >= 167837808, True)
		yield 'high_ease_spinner', name_type_map['Float'], (0, None), (False, -3.402823466e+38), (lambda context: context.version >= 167837808, True)
		yield 'interp_array_items', Array, (0, None, (None,), name_type_map['InterpBlendItem']), (False, None), (lambda context: context.version >= 167837808, True)
		yield 'interp_array_items', Array, (0, None, (None,), name_type_map['InterpBlendItem']), (False, None), (lambda context: context.version <= 167837807, None)
		yield 'manager_controlled', name_type_map['Bool'], (0, None), (False, None), (lambda context: context.version <= 167837807, None)
		yield 'weight_threshold', name_type_map['Float'], (0, None), (False, None), (lambda context: context.version <= 167837807, None)
		yield 'only_use_highest_weight', name_type_map['Bool'], (0, None), (False, None), (lambda context: context.version <= 167837807, None)
		yield 'interp_count', name_type_map['Ushort'], (0, None), (False, None), (lambda context: context.version <= 167837805, None)
		yield 'single_index', name_type_map['Ushort'], (0, None), (False, 65535), (lambda context: context.version <= 167837805, None)
		yield 'interp_count', name_type_map['Byte'], (0, None), (False, None), (lambda context: 167837806 <= context.version <= 167837807, None)
		yield 'single_index', name_type_map['Byte'], (0, None), (False, 255), (lambda context: 167837806 <= context.version <= 167837807, None)
		yield 'single_interpolator', name_type_map['Ref'], (0, name_type_map['NiInterpolator']), (False, None), (lambda context: 167837804 <= context.version <= 167837807, None)
		yield 'single_time', name_type_map['Float'], (0, None), (False, -3.402823466e+38), (lambda context: 167837804 <= context.version <= 167837807, None)
		yield 'high_priority', name_type_map['Int'], (0, None), (False, -2147483648), (lambda context: context.version <= 167837805, None)
		yield 'next_high_priority', name_type_map['Int'], (0, None), (False, -2147483648), (lambda context: context.version <= 167837805, None)
		yield 'high_priority', name_type_map['Sbyte'], (0, None), (False, -128), (lambda context: 167837806 <= context.version <= 167837807, None)
		yield 'next_high_priority', name_type_map['Sbyte'], (0, None), (False, -128), (lambda context: 167837806 <= context.version <= 167837807, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		if instance.context.version >= 167837808:
			yield 'flags', name_type_map['InterpBlendFlags'], (0, None), (False, None)
		if instance.context.version <= 167837805:
			yield 'array_size', name_type_map['Ushort'], (0, None), (False, None)
			yield 'array_grow_by', name_type_map['Ushort'], (0, None), (False, None)
		if instance.context.version >= 167837806:
			yield 'array_size', name_type_map['Byte'], (0, None), (False, None)
		if instance.context.version >= 167837808:
			yield 'weight_threshold', name_type_map['Float'], (0, None), (False, None)
		if instance.context.version >= 167837808 and not ((instance.flags & 1) != 0):
			yield 'interp_count', name_type_map['Byte'], (0, None), (False, None)
			yield 'single_index', name_type_map['Byte'], (0, None), (False, 255)
			yield 'high_priority', name_type_map['Sbyte'], (0, None), (False, -128)
			yield 'next_high_priority', name_type_map['Sbyte'], (0, None), (False, -128)
			yield 'single_time', name_type_map['Float'], (0, None), (False, -3.402823466e+38)
			yield 'high_weights_sum', name_type_map['Float'], (0, None), (False, -3.402823466e+38)
			yield 'next_high_weights_sum', name_type_map['Float'], (0, None), (False, -3.402823466e+38)
			yield 'high_ease_spinner', name_type_map['Float'], (0, None), (False, -3.402823466e+38)
			yield 'interp_array_items', Array, (0, None, (instance.array_size,), name_type_map['InterpBlendItem']), (False, None)
		if instance.context.version <= 167837807:
			yield 'interp_array_items', Array, (0, None, (instance.array_size,), name_type_map['InterpBlendItem']), (False, None)
			yield 'manager_controlled', name_type_map['Bool'], (0, None), (False, None)
			yield 'weight_threshold', name_type_map['Float'], (0, None), (False, None)
			yield 'only_use_highest_weight', name_type_map['Bool'], (0, None), (False, None)
		if instance.context.version <= 167837805:
			yield 'interp_count', name_type_map['Ushort'], (0, None), (False, None)
			yield 'single_index', name_type_map['Ushort'], (0, None), (False, 65535)
		if 167837806 <= instance.context.version <= 167837807:
			yield 'interp_count', name_type_map['Byte'], (0, None), (False, None)
			yield 'single_index', name_type_map['Byte'], (0, None), (False, 255)
		if 167837804 <= instance.context.version <= 167837807:
			yield 'single_interpolator', name_type_map['Ref'], (0, name_type_map['NiInterpolator']), (False, None)
			yield 'single_time', name_type_map['Float'], (0, None), (False, -3.402823466e+38)
		if instance.context.version <= 167837805:
			yield 'high_priority', name_type_map['Int'], (0, None), (False, -2147483648)
			yield 'next_high_priority', name_type_map['Int'], (0, None), (False, -2147483648)
		if 167837806 <= instance.context.version <= 167837807:
			yield 'high_priority', name_type_map['Sbyte'], (0, None), (False, -128)
			yield 'next_high_priority', name_type_map['Sbyte'], (0, None), (False, -128)
