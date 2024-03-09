from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiTriBasedGeom import NiTriBasedGeom


class NiTriStrips(NiTriBasedGeom):

	"""
	A shape node that refers to data organized into strips of triangles
	"""

	__name__ = 'NiTriStrips'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# Unknown bytes, all 0.
		self.unknown_q_q_speed_strip_bytes = Array(self.context, 0, None, (0,), name_type_map['Byte'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'unknown_q_q_speed_strip_bytes', Array, (0, None, (21,), name_type_map['Byte']), (False, None), (lambda context: 335676695 <= context.version <= 335676695, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		if 335676695 <= instance.context.version <= 335676695:
			yield 'unknown_q_q_speed_strip_bytes', Array, (0, None, (21,), name_type_map['Byte']), (False, None)
