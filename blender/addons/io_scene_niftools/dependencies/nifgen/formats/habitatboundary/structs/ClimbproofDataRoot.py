from nifgen.formats.habitatboundary.imports import name_type_map
from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct


class ClimbproofDataRoot(MemStruct):

	"""
	48 bytes
	"""

	__name__ = 'ClimbproofDataRoot'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# Distance between post center and start of bracket.
		self.post_gap = name_type_map['Float'](self.context, 0, None)
		self.u_1 = name_type_map['Float'].from_value(2.0)
		self.zero = name_type_map['Uint64'].from_value(0)
		self.climb_proof = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.climb_proof_cap_start = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.climb_proof_cap_end = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.climb_proof_bracket = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'climb_proof', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'climb_proof_cap_start', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'climb_proof_cap_end', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'climb_proof_bracket', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'post_gap', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'u_1', name_type_map['Float'], (0, None), (False, 2.0), (None, None)
		yield 'zero', name_type_map['Uint64'], (0, None), (True, 0), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'climb_proof', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'climb_proof_cap_start', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'climb_proof_cap_end', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'climb_proof_bracket', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'post_gap', name_type_map['Float'], (0, None), (False, None)
		yield 'u_1', name_type_map['Float'], (0, None), (False, 2.0)
		yield 'zero', name_type_map['Uint64'], (0, None), (True, 0)
