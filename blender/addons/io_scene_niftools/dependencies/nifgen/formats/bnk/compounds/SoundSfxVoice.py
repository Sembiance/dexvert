from nifgen.array import Array
from nifgen.base_struct import BaseStruct
from nifgen.formats.bnk.imports import name_type_map


class SoundSfxVoice(BaseStruct):

	__name__ = 'SoundSfxVoice'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# length of this section
		self.length = name_type_map['Uint'](self.context, 0, None)

		# id of this Sound SFX object
		self.id = name_type_map['Uint'](self.context, 0, None)

		# ?
		self.const_a = name_type_map['Uint'](self.context, 0, None)

		# ?
		self.const_b = name_type_map['Byte'](self.context, 0, None)

		# ?
		self.didx_id = name_type_map['Uint'](self.context, 0, None)

		# ?
		self.wem_length = name_type_map['Uint'](self.context, 0, None)

		# ?
		self.extra = Array(self.context, 0, None, (0,), name_type_map['Byte'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'length', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'id', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'const_a', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'const_b', name_type_map['Byte'], (0, None), (False, None), (None, None)
		yield 'didx_id', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'wem_length', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'extra', Array, (0, None, (None,), name_type_map['Byte']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'length', name_type_map['Uint'], (0, None), (False, None)
		yield 'id', name_type_map['Uint'], (0, None), (False, None)
		yield 'const_a', name_type_map['Uint'], (0, None), (False, None)
		yield 'const_b', name_type_map['Byte'], (0, None), (False, None)
		yield 'didx_id', name_type_map['Uint'], (0, None), (False, None)
		yield 'wem_length', name_type_map['Uint'], (0, None), (False, None)
		yield 'extra', Array, (0, None, (instance.length - 17,), name_type_map['Byte']), (False, None)
