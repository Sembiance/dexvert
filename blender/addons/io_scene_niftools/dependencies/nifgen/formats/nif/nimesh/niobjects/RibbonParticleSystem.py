from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nipsparticle.niobjects.NiPSParticleSystem import NiPSParticleSystem


class RibbonParticleSystem(NiPSParticleSystem):

	"""
	Epic Mickey specific block.
	"""

	__name__ = 'RibbonParticleSystem'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.em_unknown_bytes_1 = Array(self.context, 0, None, (0,), name_type_map['Byte'])
		self.em_unknown_float_1 = name_type_map['Float'](self.context, 0, None)
		self.em_unknown_bytes_2 = Array(self.context, 0, None, (0,), name_type_map['Byte'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'em_unknown_bytes_1', Array, (0, None, (6,), name_type_map['Byte']), (False, None), (None, None)
		yield 'em_unknown_float_1', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'em_unknown_bytes_2', Array, (0, None, (4,), name_type_map['Byte']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'em_unknown_bytes_1', Array, (0, None, (6,), name_type_map['Byte']), (False, None)
		yield 'em_unknown_float_1', name_type_map['Float'], (0, None), (False, None)
		yield 'em_unknown_bytes_2', Array, (0, None, (4,), name_type_map['Byte']), (False, None)
