from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class TriangleData(BaseStruct):

	"""
	Bethesda Havok. A triangle with extra data used for physics.
	"""

	__name__ = 'TriangleData'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# The triangle.
		self.triangle = name_type_map['Triangle'](self.context, 0, None)

		# Additional havok information on how triangles are welded.
		self.welding_info = name_type_map['BhkWeldInfo'](self.context, 0, None)

		# This is the triangle's normal.
		self.normal = name_type_map['Vector3'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'triangle', name_type_map['Triangle'], (0, None), (False, None), (None, None)
		yield 'welding_info', name_type_map['BhkWeldInfo'], (0, None), (False, None), (None, None)
		yield 'normal', name_type_map['Vector3'], (0, None), (False, None), (lambda context: context.version <= 335544325, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'triangle', name_type_map['Triangle'], (0, None), (False, None)
		yield 'welding_info', name_type_map['BhkWeldInfo'], (0, None), (False, None)
		if instance.context.version <= 335544325:
			yield 'normal', name_type_map['Vector3'], (0, None), (False, None)
