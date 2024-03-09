from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class NiPlane(BaseStruct):

	"""
	A plane.
	"""

	__name__ = 'NiPlane'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# The plane normal.
		self.normal = name_type_map['Vector3'](self.context, 0, None)

		# The plane constant.
		self.constant = name_type_map['Float'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'normal', name_type_map['Vector3'], (0, None), (False, None), (None, None)
		yield 'constant', name_type_map['Float'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'normal', name_type_map['Vector3'], (0, None), (False, None)
		yield 'constant', name_type_map['Float'], (0, None), (False, None)
