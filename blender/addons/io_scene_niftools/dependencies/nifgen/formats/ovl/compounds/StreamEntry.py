from nifgen.base_struct import BaseStruct
from nifgen.formats.ovl.imports import name_type_map


class StreamEntry(BaseStruct):

	"""
	Description of one streamed file instance. One for every file stored in an ovs.
	Links the main pointers of a streamed file to its user, eg. a texturestream to a tex file.
	--These appear sorted in the order of root entries per ovs.-- only true for lod0, not lod1
	the order does not seem to be consistent
	interestingly, the order of root_entry entries per ovs is consistent with decreasing pool offset
	"""

	__name__ = 'StreamEntry'

	allow_np = True

	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# offset to the stream's root_entry pointer inside the flattened mempools
		self.stream_offset = name_type_map['Uint'](self.context, 0, None)

		# offset to the user file's root_entry pointer (in STATIC) inside the flattened mempools
		self.file_offset = name_type_map['Uint'](self.context, 0, None)
		self.zero = name_type_map['Uint'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'stream_offset', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'file_offset', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'zero', name_type_map['Uint'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'stream_offset', name_type_map['Uint'], (0, None), (False, None)
		yield 'file_offset', name_type_map['Uint'], (0, None), (False, None)
		yield 'zero', name_type_map['Uint'], (0, None), (False, None)
