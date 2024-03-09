import logging

from nifgen.array import Array
from nifgen.formats.ovl_base.compounds.ArrayPointer import ArrayPointer
from nifgen.formats.ovl_base.compounds.ForEachPointer import ForEachPointer
from nifgen.formats.ovl_base.compounds.CondPointer import CondPointer
from nifgen.formats.ovl_base.compounds.Pointer import Pointer

DEPENDENCY_TAG = "dependency"


from nifgen.base_struct import BaseStruct


class MemStruct(BaseStruct):

	"""
	this is a struct that is capable of having pointers
	"""

	__name__ = 'MemStruct'


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

	def write_ptrs(self, loader, pool):
		"""Process all pointers in the structure and recursively load pointers in the sub-structs."""
		# recursive doesnt get the whole structure - why?
		# could work if the order is good
		pool.offsets.add(self.io_start)
		pool.size_map[self.io_start] = self.io_size
		children = loader.stack[(pool, self.io_start)] = {}
		for ptr, f_name, arguments in MemStruct.get_instances_recursive(self, Pointer):
			# when an array is entered
			# locates the read address, attaches the frag entry, and reads the template as ptr.data
			offset = ptr.io_start
			rel_offset = offset - self.io_start
			# logging.debug(f"Pointer {f_name}, has_data {ptr.has_data} at {ptr.io_start}, relative {rel_offset}")
			# when it's a pointer in an array, f_name is the array index
			if isinstance(f_name, str) and DEPENDENCY_TAG in f_name:
				if ptr.data:
					# loader.dependencies[ptr.data] = (pool, offset)
					loader.dependencies.append((ptr.data, (pool, offset)))
					pool.offset_2_link[offset] = ptr.data
			elif ptr.has_data:
				ptr.write_ptr(loader, pool)
				# store relative offset from this memstruct
				children[rel_offset] = (ptr.target_pool, ptr.target_offset)
				# keep reading pointers in the newly read ptr.data
				for memstruct in self.structs_from_ptr(ptr):
					memstruct.write_ptrs(loader, ptr.target_pool)

	@classmethod
	def get_instances_recursive(cls, instance, dtype):
		for s_type, s_inst, (f_name, f_type, arguments, _) in cls.get_condition_attributes_recursive(instance, instance, lambda x: issubclass(x[1], dtype)):
			f_inst = s_type.get_field(s_inst, f_name)
			yield f_inst, f_name, arguments

	def read_ptrs(self, pool, debug=False):
		"""Process all pointers in the structure and recursively load pointers in the sub-structs."""
		offsets_of_ptrs = set()
		# need to recurse here, because we may have substructs that are part of this MemStruct (not via ptrs)
		for ptr, f_name, arguments in MemStruct.get_instances_recursive(self, Pointer):
			# update the pointer's arg, as it is sometimes read after the pointer
			ptr.arg, template = arguments
			if not ptr.template:
				# try the lookup function to get a suitable template for this field
				ptr.template = self.get_ptr_template(f_name)
			offsets_of_ptrs.add(ptr.io_start)
			# locates the read address, attaches the frag entry, and reads the template as ptr.data
			ptr.read_ptr(pool)
			if ptr.target_pool:
				# keep reading pointers in the newly read ptr.data
				for memstruct in self.structs_from_ptr(ptr):
					memstruct.read_ptrs(ptr.target_pool, debug=debug)
		if debug:
			# verify that there is no uncaught pointer
			for l_offset, rel_offset, entry in pool.get_ptrs_in_struct(self.io_start, self.io_size):
				# skip dependencies
				if isinstance(entry, tuple):
					target_pool, target_offset = entry
					if l_offset not in offsets_of_ptrs:
						logging.warning(f"Pointer at {pool.i} | {l_offset} to {target_pool.i} | {target_offset} is missing for {self.__class__.__name__} (rel offset: {rel_offset})")

	@staticmethod
	def structs_from_ptr(ptr):
		"""Get all direct memstruct children of this ptr"""
		if isinstance(ptr.data, MemStruct):
			yield ptr.data
		elif isinstance(ptr.data, Array):
			assert isinstance(ptr, (ArrayPointer, ForEachPointer, CondPointer))
			for member in ptr.data:
				if isinstance(member, MemStruct):
					yield member

	def get_ptr_template(self, prop):
		"""Returns the appropriate template for a pointer named 'prop', if exists.
		Must be overwritten in subclass"""
		return None


