from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nianimation.niobjects.NiExtraDataController import NiExtraDataController


class NiFloatExtraDataController(NiExtraDataController):

	"""
	Animates an NiFloatExtraData object attached to an NiAVObject.
	NiInterpController::GetCtlrID() string format is same as parent.
	"""

	__name__ = 'NiFloatExtraDataController'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# Number of extra bytes.
		self.num_extra_bytes = name_type_map['Byte'](self.context, 0, None)
		self.unknown_bytes = Array(self.context, 0, None, (0,), name_type_map['Byte'])
		self.unknown_extra_bytes = Array(self.context, 0, None, (0,), name_type_map['Byte'])
		self.data = name_type_map['Ref'](self.context, 0, name_type_map['NiFloatData'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'num_extra_bytes', name_type_map['Byte'], (0, None), (False, None), (lambda context: context.version <= 167837696, None)
		yield 'unknown_bytes', Array, (0, None, (7,), name_type_map['Byte']), (False, None), (lambda context: context.version <= 167837696, None)
		yield 'unknown_extra_bytes', Array, (0, None, (None,), name_type_map['Byte']), (False, None), (lambda context: context.version <= 167837696, None)
		yield 'data', name_type_map['Ref'], (0, name_type_map['NiFloatData']), (False, None), (lambda context: context.version <= 167837799, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		if instance.context.version <= 167837696:
			yield 'num_extra_bytes', name_type_map['Byte'], (0, None), (False, None)
			yield 'unknown_bytes', Array, (0, None, (7,), name_type_map['Byte']), (False, None)
			yield 'unknown_extra_bytes', Array, (0, None, (instance.num_extra_bytes,), name_type_map['Byte']), (False, None)
		if instance.context.version <= 167837799:
			yield 'data', name_type_map['Ref'], (0, name_type_map['NiFloatData']), (False, None)
