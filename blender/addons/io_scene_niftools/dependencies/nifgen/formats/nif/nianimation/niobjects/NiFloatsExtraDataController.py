from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nianimation.niobjects.NiExtraDataController import NiExtraDataController


class NiFloatsExtraDataController(NiExtraDataController):

	"""
	Animates an NiFloatsExtraData object attached to an NiAVObject.
	NiInterpController::GetCtlrID() string format:
	'%s[%d]'
	Where %s = Value of "Extra Data Name", %d = Value of "Floats Extra Data Index"
	"""

	__name__ = 'NiFloatsExtraDataController'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.floats_extra_data_index = name_type_map['Int'](self.context, 0, None)
		self.data = name_type_map['Ref'](self.context, 0, name_type_map['NiFloatData'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'floats_extra_data_index', name_type_map['Int'], (0, None), (False, None), (None, None)
		yield 'data', name_type_map['Ref'], (0, name_type_map['NiFloatData']), (False, None), (lambda context: context.version <= 167837799, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'floats_extra_data_index', name_type_map['Int'], (0, None), (False, None)
		if instance.context.version <= 167837799:
			yield 'data', name_type_map['Ref'], (0, name_type_map['NiFloatData']), (False, None)
