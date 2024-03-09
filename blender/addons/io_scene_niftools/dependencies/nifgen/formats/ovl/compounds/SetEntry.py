from nifgen.base_struct import BaseStruct
from nifgen.formats.ovl.imports import name_type_map


class SetEntry(BaseStruct):

	"""
	the asset indices of two consecutive SetEntries define a set of AssetEntries
	"""

	__name__ = 'SetEntry'

	allow_np = True

	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.file_hash = name_type_map['Uint'](self.context, 0, None)
		self.ext_hash = name_type_map['Uint'](self.context, 0, None)

		# add assets from last set's start up to this index to this set
		self.start = name_type_map['Uint'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'file_hash', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'ext_hash', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.version >= 19, None)
		yield 'start', name_type_map['Uint'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'file_hash', name_type_map['Uint'], (0, None), (False, None)
		if instance.context.version >= 19:
			yield 'ext_hash', name_type_map['Uint'], (0, None), (False, None)
		yield 'start', name_type_map['Uint'], (0, None), (False, None)
