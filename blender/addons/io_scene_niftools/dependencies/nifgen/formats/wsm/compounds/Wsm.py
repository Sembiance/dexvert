from nifgen.array import Array
from nifgen.formats.ovl_base.compounds.GenericHeader import GenericHeader
from nifgen.formats.wsm.imports import name_type_map


class Wsm(GenericHeader):

	__name__ = 'Wsm'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.header = name_type_map['WsmHeader'](self.context, 0, None)

		# xyz
		self.locs = Array(self.context, 0, None, (0,), name_type_map['Float'])

		# xyzw
		self.quats = Array(self.context, 0, None, (0,), name_type_map['Float'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'header', name_type_map['WsmHeader'], (0, None), (False, None), (None, None)
		yield 'locs', Array, (0, None, (None, 3,), name_type_map['Float']), (False, None), (None, None)
		yield 'quats', Array, (0, None, (None, 4,), name_type_map['Float']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'header', name_type_map['WsmHeader'], (0, None), (False, None)
		yield 'locs', Array, (0, None, (instance.header.frame_count, 3,), name_type_map['Float']), (False, None)
		yield 'quats', Array, (0, None, (instance.header.frame_count, 4,), name_type_map['Float']), (False, None)
