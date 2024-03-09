from nifgen.base_struct import BaseStruct


class AbstractPointer(BaseStruct):

	"""
	forward pointing, of varying size
	"""

	__name__ = 'AbstractPointer'


	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)

	def __init__(self, context, arg=None, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.joint = None
		if set_default:
			self.set_defaults()

	def __repr__(self):
		n = self.joint.name if self.joint else None
		return f"{self.index} -> {n}"

