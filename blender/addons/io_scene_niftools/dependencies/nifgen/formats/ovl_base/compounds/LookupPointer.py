from nifgen.formats.ovl_base.compounds.Pointer import Pointer

from nifgen.formats.ovl_base.compounds.Pointer import Pointer


class LookupPointer(Pointer):

	__name__ = 'LookupPointer'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)

	def update_index(self, array):
		# check if own data has been read at same memory address as member of the array
		for i, member in enumerate(array):
			if self.data.io_start == member.io_start:
				self.pool_index = i

	def update_target(self, array_ptr):
		# set own data, then clear pool index
		self.data = array_ptr.data[self.pool_index]
		self.array_ptr = array_ptr
		self.pool_index = 0

	def write_ptr(self, loader, src_pool):
		"""Lookup pointer data should never be written, as it indexes into an array already written by another pointer"""
		loader.attach_frag_to_ptr(src_pool, self.io_start, self.array_ptr.target_pool, self.data.io_start)

