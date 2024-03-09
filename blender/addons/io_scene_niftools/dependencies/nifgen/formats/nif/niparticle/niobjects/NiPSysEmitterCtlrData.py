from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiObject import NiObject


class NiPSysEmitterCtlrData(NiObject):

	"""
	DEPRECATED (10.2). Particle system emitter controller data.
	"""

	__name__ = 'NiPSysEmitterCtlrData'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.birth_rate_keys = name_type_map['KeyGroup'](self.context, 0, name_type_map['Float'])
		self.num_active_keys = name_type_map['Uint'](self.context, 0, None)
		self.active_keys = Array(self.context, 1, name_type_map['Byte'], (0,), name_type_map['Key'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'birth_rate_keys', name_type_map['KeyGroup'], (0, name_type_map['Float']), (False, None), (None, None)
		yield 'num_active_keys', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'active_keys', Array, (1, name_type_map['Byte'], (None,), name_type_map['Key']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'birth_rate_keys', name_type_map['KeyGroup'], (0, name_type_map['Float']), (False, None)
		yield 'num_active_keys', name_type_map['Uint'], (0, None), (False, None)
		yield 'active_keys', Array, (1, name_type_map['Byte'], (instance.num_active_keys,), name_type_map['Key']), (False, None)
