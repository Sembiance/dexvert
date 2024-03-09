from nifgen.formats.nif.bsmain.niobjects.BSMultiBoundData import BSMultiBoundData
from nifgen.formats.nif.imports import name_type_map


class BSMultiBoundOBB(BSMultiBoundData):

	"""
	Oriented bounding box.
	"""

	__name__ = 'BSMultiBoundOBB'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# Center of the box.
		self.center = name_type_map['Vector3'](self.context, 0, None)

		# Size of the box along each axis.
		self.size = name_type_map['Vector3'](self.context, 0, None)

		# Rotation of the bounding box.
		self.rotation = name_type_map['Matrix33'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'center', name_type_map['Vector3'], (0, None), (False, None), (None, None)
		yield 'size', name_type_map['Vector3'], (0, None), (False, None), (None, None)
		yield 'rotation', name_type_map['Matrix33'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'center', name_type_map['Vector3'], (0, None), (False, None)
		yield 'size', name_type_map['Vector3'], (0, None), (False, None)
		yield 'rotation', name_type_map['Matrix33'], (0, None), (False, None)
