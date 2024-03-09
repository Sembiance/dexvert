from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiObject import NiObject


class NiVisData(NiObject):

	"""
	DEPRECATED (10.2), REMOVED (?), Replaced by NiBoolData.
	Visibility data for a controller.
	"""

	__name__ = 'NiVisData'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.num_keys = name_type_map['Uint'](self.context, 0, None)
		self.keys = Array(self.context, 1, name_type_map['Byte'], (0,), name_type_map['Key'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'num_keys', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'keys', Array, (1, name_type_map['Byte'], (None,), name_type_map['Key']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'num_keys', name_type_map['Uint'], (0, None), (False, None)
		yield 'keys', Array, (1, name_type_map['Byte'], (instance.num_keys,), name_type_map['Key']), (False, None)
