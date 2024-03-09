from nifgen.array import Array
from nifgen.formats.nif.bshavok.niobjects.BhkUnaryAction import BhkUnaryAction
from nifgen.formats.nif.imports import name_type_map


class BhkOrientHingedBodyAction(BhkUnaryAction):

	"""
	Bethesda extension of hkpReorientAction (or similar). Will try to reorient a body to stay facing a given direction.
	"""

	__name__ = 'bhkOrientHingedBodyAction'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.unused_02 = Array(self.context, 0, None, (0,), name_type_map['Byte'])
		self.hinge_axis_ls = name_type_map['Vector4'].from_value((1.0, 0.0, 0.0, 0.0))
		self.forward_ls = name_type_map['Vector4'].from_value((0.0, 1.0, 0.0, 0.0))
		self.strength = name_type_map['Float'].from_value(1.0)
		self.damping = name_type_map['Float'].from_value(0.1)
		self.unused_03 = Array(self.context, 0, None, (0,), name_type_map['Byte'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'unused_02', Array, (0, None, (8,), name_type_map['Byte']), (False, None), (None, None)
		yield 'hinge_axis_ls', name_type_map['Vector4'], (0, None), (False, (1.0, 0.0, 0.0, 0.0)), (None, None)
		yield 'forward_ls', name_type_map['Vector4'], (0, None), (False, (0.0, 1.0, 0.0, 0.0)), (None, None)
		yield 'strength', name_type_map['Float'], (0, None), (False, 1.0), (None, None)
		yield 'damping', name_type_map['Float'], (0, None), (False, 0.1), (None, None)
		yield 'unused_03', Array, (0, None, (8,), name_type_map['Byte']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'unused_02', Array, (0, None, (8,), name_type_map['Byte']), (False, None)
		yield 'hinge_axis_ls', name_type_map['Vector4'], (0, None), (False, (1.0, 0.0, 0.0, 0.0))
		yield 'forward_ls', name_type_map['Vector4'], (0, None), (False, (0.0, 1.0, 0.0, 0.0))
		yield 'strength', name_type_map['Float'], (0, None), (False, 1.0)
		yield 'damping', name_type_map['Float'], (0, None), (False, 0.1)
		yield 'unused_03', Array, (0, None, (8,), name_type_map['Byte']), (False, None)
