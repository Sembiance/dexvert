from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiProperty import NiProperty


class NiTextureProperty(NiProperty):

	"""
	LEGACY (pre-10.1)
	"""

	__name__ = 'NiTextureProperty'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.unknown_ints_1 = Array(self.context, 0, None, (0,), name_type_map['Uint'])

		# Property flags.
		self.flags = name_type_map['Ushort'](self.context, 0, None)

		# Link to the texture image.
		self.image = name_type_map['Ref'](self.context, 0, name_type_map['NiImage'])
		self.unknown_ints_2 = Array(self.context, 0, None, (0,), name_type_map['Uint'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'unknown_ints_1', Array, (0, None, (2,), name_type_map['Uint']), (False, None), (lambda context: context.version <= 33751040, None)
		yield 'flags', name_type_map['Ushort'], (0, None), (False, None), (lambda context: context.version >= 50331648, None)
		yield 'image', name_type_map['Ref'], (0, name_type_map['NiImage']), (False, None), (None, None)
		yield 'unknown_ints_2', Array, (0, None, (2,), name_type_map['Uint']), (False, None), (lambda context: 50331648 <= context.version <= 50332416, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		if instance.context.version <= 33751040:
			yield 'unknown_ints_1', Array, (0, None, (2,), name_type_map['Uint']), (False, None)
		if instance.context.version >= 50331648:
			yield 'flags', name_type_map['Ushort'], (0, None), (False, None)
		yield 'image', name_type_map['Ref'], (0, name_type_map['NiImage']), (False, None)
		if 50331648 <= instance.context.version <= 50332416:
			yield 'unknown_ints_2', Array, (0, None, (2,), name_type_map['Uint']), (False, None)
