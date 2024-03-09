from nifgen.array import Array
from nifgen.formats.ovl_base.compounds.Pointer import Pointer
from nifgen.formats.ovl_base.compounds.Pointer import Pointer


class ArrayPointer(Pointer):

	"""
	a pointer to an array in an ovl memory layout
	"""

	__name__ = 'ArrayPointer'


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

	@property
	def has_data(self):
		"""Returns True if it has data"""
		# fdev create pointers to empty arrays
		if self.data is not None:
			return True
			# return len(self.data)

	def read_template(self, stream):
		if self.template:
			self.data = Array.from_stream(stream, self.context, 0, None, (self.arg,), self.template)

	@classmethod
	def _to_xml(cls, instance, elem, debug):
		"""Assigns data self to xml elem"""
		if callable(getattr(instance.template, "_to_xml_array", None)):
			instance.template._to_xml_array(instance.data, elem, debug)
			return
		Array._to_xml(instance.data, elem, debug)

	@classmethod
	def _from_xml(cls, instance, elem):
		if callable(getattr(instance.template, "_from_xml_array", None)):
			instance.data = instance.template._from_xml_array(None, elem)
			return
		arr = Array(instance.context, 0, None, (len(elem)), instance.template, set_default=False)
		instance.data = Array._from_xml(arr, elem)
		return instance

