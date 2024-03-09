from nifgen.base_struct import BaseStruct
from nifgen.formats.ms2.imports import name_type_map


class Capsule(BaseStruct):

	__name__ = 'Capsule'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# relative to the armature, ie. not in bone space
		self.offset = name_type_map['Vector3'](self.context, 0, None)

		# normalized
		self.direction = name_type_map['Vector3'](self.context, 0, None)

		# radius of the caps
		self.radius = name_type_map['Float'](self.context, 0, None)

		# distance between the center points of the capsule caps, total extent is 2 * radius + extent
		self.extent = name_type_map['Float'](self.context, 0, None)

		# apparently unused
		self.zero = name_type_map['Uint'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'offset', name_type_map['Vector3'], (0, None), (False, None), (None, None)
		yield 'direction', name_type_map['Vector3'], (0, None), (False, None), (None, None)
		yield 'radius', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'extent', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'zero', name_type_map['Uint'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'offset', name_type_map['Vector3'], (0, None), (False, None)
		yield 'direction', name_type_map['Vector3'], (0, None), (False, None)
		yield 'radius', name_type_map['Float'], (0, None), (False, None)
		yield 'extent', name_type_map['Float'], (0, None), (False, None)
		yield 'zero', name_type_map['Uint'], (0, None), (False, None)
