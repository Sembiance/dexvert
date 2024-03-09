import xml.etree.ElementTree as ET
from nifgen.array import Array
from nifgen.formats.ovl_base.compounds.Pointer import Pointer

XML_STR = "xml_string"
from nifgen.formats.ovl_base.compounds.Pointer import Pointer


class CondPointer(Pointer):

	"""
	a pointer to a data struct that may sometimes be null without a bool
	"""

	__name__ = 'CondPointer'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)

	@classmethod
	def to_xml(cls, elem, prop, instance, arg, template, debug):
		"""Adds this struct to 'elem', recursively"""
		if instance.has_data:
			sub = ET.SubElement(elem, prop)
			cls.pool_type_to_xml(sub, instance, debug)
			# xml string
			if prop == XML_STR:
				sub.append(ET.fromstring(instance.data))
			else:
				cls._to_xml(instance, sub, debug)

