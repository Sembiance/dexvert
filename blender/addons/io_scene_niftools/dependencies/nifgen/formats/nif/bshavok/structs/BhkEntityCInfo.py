from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class BhkEntityCInfo(BaseStruct):

	__name__ = 'bhkEntityCInfo'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# How the body reacts to collisions. See hkResponseType for hkpWorld default implementations.
		self.collision_response = name_type_map['HkResponseType'].RESPONSE_SIMPLE_CONTACT
		self.unused_01 = name_type_map['Byte'](self.context, 0, None)

		# Lowers the frequency for processContactCallbacks. A value of 5 means that a callback is raised every 5th frame. The default is once every 65535 frames.
		self.process_contact_callback_delay = name_type_map['Ushort'].from_value(65535)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'collision_response', name_type_map['HkResponseType'], (0, None), (False, name_type_map['HkResponseType'].RESPONSE_SIMPLE_CONTACT), (None, None)
		yield 'unused_01', name_type_map['Byte'], (0, None), (False, None), (None, None)
		yield 'process_contact_callback_delay', name_type_map['Ushort'], (0, None), (False, 65535), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'collision_response', name_type_map['HkResponseType'], (0, None), (False, name_type_map['HkResponseType'].RESPONSE_SIMPLE_CONTACT)
		yield 'unused_01', name_type_map['Byte'], (0, None), (False, None)
		yield 'process_contact_callback_delay', name_type_map['Ushort'], (0, None), (False, 65535)
