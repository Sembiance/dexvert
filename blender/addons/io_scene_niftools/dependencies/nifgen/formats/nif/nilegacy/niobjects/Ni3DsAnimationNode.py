from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiObject import NiObject


class Ni3DsAnimationNode(NiObject):

	"""
	Unknown. Only found in 2.3 nifs.
	"""

	__name__ = 'Ni3dsAnimationNode'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# Name of this object.
		self.name = name_type_map['SizedString'](self.context, 0, None)
		self.has_data = name_type_map['Bool'](self.context, 0, None)
		self.unknown_floats_1 = Array(self.context, 0, None, (0,), name_type_map['Float'])
		self.unknown_short = name_type_map['Ushort'](self.context, 0, None)
		self.child = name_type_map['Ref'](self.context, 0, name_type_map['NiObject'])
		self.unknown_floats_2 = Array(self.context, 0, None, (0,), name_type_map['Float'])

		# A count.
		self.count = name_type_map['Uint'](self.context, 0, None)
		self.unknown_array = Array(self.context, 0, None, (0,), name_type_map['Byte'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'name', name_type_map['SizedString'], (0, None), (False, None), (None, None)
		yield 'has_data', name_type_map['Bool'], (0, None), (False, None), (None, None)
		yield 'unknown_floats_1', Array, (0, None, (21,), name_type_map['Float']), (False, None), (None, True)
		yield 'unknown_short', name_type_map['Ushort'], (0, None), (False, None), (None, True)
		yield 'child', name_type_map['Ref'], (0, name_type_map['NiObject']), (False, None), (None, True)
		yield 'unknown_floats_2', Array, (0, None, (12,), name_type_map['Float']), (False, None), (None, True)
		yield 'count', name_type_map['Uint'], (0, None), (False, None), (None, True)
		yield 'unknown_array', Array, (0, None, (None, 5,), name_type_map['Byte']), (False, None), (None, True)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'name', name_type_map['SizedString'], (0, None), (False, None)
		yield 'has_data', name_type_map['Bool'], (0, None), (False, None)
		if instance.has_data:
			yield 'unknown_floats_1', Array, (0, None, (21,), name_type_map['Float']), (False, None)
			yield 'unknown_short', name_type_map['Ushort'], (0, None), (False, None)
			yield 'child', name_type_map['Ref'], (0, name_type_map['NiObject']), (False, None)
			yield 'unknown_floats_2', Array, (0, None, (12,), name_type_map['Float']), (False, None)
			yield 'count', name_type_map['Uint'], (0, None), (False, None)
			yield 'unknown_array', Array, (0, None, (instance.count, 5,), name_type_map['Byte']), (False, None)
