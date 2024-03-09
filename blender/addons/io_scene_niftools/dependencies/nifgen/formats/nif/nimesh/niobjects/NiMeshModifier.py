from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiObject import NiObject


class NiMeshModifier(NiObject):

	"""
	Base class for mesh modifiers.
	"""

	__name__ = 'NiMeshModifier'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.num_submit_points = name_type_map['Uint'](self.context, 0, None)

		# The sync points supported by this mesh modifier for SubmitTasks.
		self.submit_points = Array(self.context, 0, None, (0,), name_type_map['SyncPoint'])
		self.num_complete_points = name_type_map['Uint'](self.context, 0, None)

		# The sync points supported by this mesh modifier for CompleteTasks.
		self.complete_points = Array(self.context, 0, None, (0,), name_type_map['SyncPoint'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'num_submit_points', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'submit_points', Array, (0, None, (None,), name_type_map['SyncPoint']), (False, None), (None, None)
		yield 'num_complete_points', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'complete_points', Array, (0, None, (None,), name_type_map['SyncPoint']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'num_submit_points', name_type_map['Uint'], (0, None), (False, None)
		yield 'submit_points', Array, (0, None, (instance.num_submit_points,), name_type_map['SyncPoint']), (False, None)
		yield 'num_complete_points', name_type_map['Uint'], (0, None), (False, None)
		yield 'complete_points', Array, (0, None, (instance.num_complete_points,), name_type_map['SyncPoint']), (False, None)
