from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiTimeController import NiTimeController


class NiFurSpringController(NiTimeController):

	"""
	Blood Bowl Specific
	Used on things like hair/tails in conjunction with bones to animate them.
	"""

	__name__ = 'NiFurSpringController'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.unknown_float = name_type_map['Float'](self.context, 0, None)
		self.unknown_float_2 = name_type_map['Float'](self.context, 0, None)

		# The number of node bones referenced as influences.
		self.num_bones = name_type_map['Uint'](self.context, 0, None)

		# List of all armature bones.
		self.bones = Array(self.context, 0, name_type_map['NiNode'], (0,), name_type_map['Ptr'])

		# The number of node bones referenced as influences.
		self.num_bones_2 = name_type_map['Uint'](self.context, 0, None)

		# List of all armature bones.
		self.bones_2 = Array(self.context, 0, name_type_map['NiNode'], (0,), name_type_map['Ptr'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'unknown_float', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'unknown_float_2', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'num_bones', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'bones', Array, (0, name_type_map['NiNode'], (None,), name_type_map['Ptr']), (False, None), (None, None)
		yield 'num_bones_2', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'bones_2', Array, (0, name_type_map['NiNode'], (None,), name_type_map['Ptr']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'unknown_float', name_type_map['Float'], (0, None), (False, None)
		yield 'unknown_float_2', name_type_map['Float'], (0, None), (False, None)
		yield 'num_bones', name_type_map['Uint'], (0, None), (False, None)
		yield 'bones', Array, (0, name_type_map['NiNode'], (instance.num_bones,), name_type_map['Ptr']), (False, None)
		yield 'num_bones_2', name_type_map['Uint'], (0, None), (False, None)
		yield 'bones_2', Array, (0, name_type_map['NiNode'], (instance.num_bones_2,), name_type_map['Ptr']), (False, None)
