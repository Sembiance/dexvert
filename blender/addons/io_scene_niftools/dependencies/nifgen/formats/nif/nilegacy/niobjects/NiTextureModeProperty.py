from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiProperty import NiProperty


class NiTextureModeProperty(NiProperty):

	"""
	LEGACY (pre-10.1)
	"""

	__name__ = 'NiTextureModeProperty'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.unknown_ints = Array(self.context, 0, None, (0,), name_type_map['Uint'])

		# Either 210 or 194.
		self.flags = name_type_map['Ushort'](self.context, 0, None)
		self.ps_2_l = name_type_map['Short'].from_value(0)
		self.ps_2_k = name_type_map['Short'].from_value(-75)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'unknown_ints', Array, (0, None, (3,), name_type_map['Uint']), (False, None), (lambda context: context.version <= 33751040, None)
		yield 'flags', name_type_map['Ushort'], (0, None), (False, None), (lambda context: context.version >= 50331648, None)
		yield 'ps_2_l', name_type_map['Short'], (0, None), (False, 0), (lambda context: 50397184 <= context.version <= 167903232, None)
		yield 'ps_2_k', name_type_map['Short'], (0, None), (False, -75), (lambda context: 50397184 <= context.version <= 167903232, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		if instance.context.version <= 33751040:
			yield 'unknown_ints', Array, (0, None, (3,), name_type_map['Uint']), (False, None)
		if instance.context.version >= 50331648:
			yield 'flags', name_type_map['Ushort'], (0, None), (False, None)
		if 50397184 <= instance.context.version <= 167903232:
			yield 'ps_2_l', name_type_map['Short'], (0, None), (False, 0)
			yield 'ps_2_k', name_type_map['Short'], (0, None), (False, -75)
