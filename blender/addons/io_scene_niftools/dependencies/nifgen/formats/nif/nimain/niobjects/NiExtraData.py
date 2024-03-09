from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiObject import NiObject


class NiExtraData(NiObject):

	"""
	A generic extra data object.
	"""

	__name__ = 'NiExtraData'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# Name of this object.
		self.name = name_type_map['String'](self.context, 0, None)

		# Block number of the next extra data object.
		self.next_extra_data = name_type_map['Ref'](self.context, 0, name_type_map['NiExtraData'])

		# The extra data was sometimes stored as binary directly on NiExtraData.
		self.extra_data = name_type_map['ByteArray'](self.context, 0, None)

		# Ignore binary data after 4.x as the child block will cover it.
		self.num_bytes = name_type_map['Uint'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'name', name_type_map['String'], (0, None), (False, None), (lambda context: context.version >= 167772416, True)
		yield 'next_extra_data', name_type_map['Ref'], (0, name_type_map['NiExtraData']), (False, None), (lambda context: context.version <= 67240448, None)
		yield 'extra_data', name_type_map['ByteArray'], (0, None), (False, None), (lambda context: context.version <= 50528269, None)
		yield 'num_bytes', name_type_map['Uint'], (0, None), (False, None), (lambda context: 67108864 <= context.version <= 67240448, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		if instance.context.version >= 167772416 and not isinstance(instance, name_type_map['BSExtraData']):
			yield 'name', name_type_map['String'], (0, None), (False, None)
		if instance.context.version <= 67240448:
			yield 'next_extra_data', name_type_map['Ref'], (0, name_type_map['NiExtraData']), (False, None)
		if instance.context.version <= 50528269:
			yield 'extra_data', name_type_map['ByteArray'], (0, None), (False, None)
		if 67108864 <= instance.context.version <= 67240448:
			yield 'num_bytes', name_type_map['Uint'], (0, None), (False, None)
