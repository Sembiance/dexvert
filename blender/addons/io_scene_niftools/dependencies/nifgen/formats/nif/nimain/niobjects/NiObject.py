from nifgen.array import Array
from nifgen.bitfield import BasicBitfield
from nifgen.base_enum import BaseEnum
import nifgen.formats.nif as NifFormat
from nifgen.formats.nif.basic import Ref, Ptr
from nifgen.base_struct import BaseStruct


class NiObject(BaseStruct):

	"""
	Abstract object type.
	"""

	__name__ = 'NiObject'


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
	def find(self, block_name = None, block_type = None):
		# does this block match the search criteria?
		if block_name and block_type:
			if isinstance(self, block_type):
				try:
					if block_name == self.name: return self
				except AttributeError:
					pass
		elif block_name:
			try:
				if block_name == self.name: return self
			except AttributeError:
				pass
		elif block_type:
			if isinstance(self, block_type): return self

		# ok, this block is not a match, so check further down in tree
		for child in self.get_refs():
			blk = child.find(block_name, block_type)
			if blk: return blk

		return None

	def find_chain(self, block, block_type = None):
		"""Finds a chain of blocks going from C{self} to C{block}. If found,
		self is the first element and block is the last element. If no branch
		found, returns an empty list. Does not check whether there is more
		than one branch; if so, the first one found is returned.

		:param block: The block to find a chain to.
		:param block_type: The type that blocks should have in this chain."""

		if self is block: return [self]
		for child in self.get_refs():
			if block_type and not isinstance(child, block_type): continue
			child_chain = child.find_chain(block, block_type)
			if child_chain:
				return [self] + child_chain

		return []

	def apply_scale(self, scale):
		"""Scale data in this block. This implementation does nothing.
		Override this method if it contains geometry data that can be
		scaled.
		"""
		pass


	def get_links(self):
		def field_has_links(attr_def):
			if issubclass(attr_def[1], Array):
				f_type = attr_def[2][3]
			else:
				f_type = attr_def[1]
			return f_type._has_links
		condition_function = lambda x: issubclass(x[1], (Ref, Ptr))
		for val in BaseStruct.get_condition_values_recursive(self, condition_function, enter_condition=field_has_links):
			if val is not None:
				yield val

	def get_refs(self):
		def field_has_refs(attr_def):
			if issubclass(attr_def[1], Array):
				f_type = attr_def[2][3]
			else:
				f_type = attr_def[1]
			return f_type._has_refs
		condition_function = lambda x: issubclass(x[1], Ref)
		for val in BaseStruct.get_condition_values_recursive(self, condition_function, enter_condition=field_has_refs):
			if val is not None:
				yield val

	def tree(self, block_type=None, follow_all=True, unique=False):
		"""A generator for parsing all blocks in the tree (starting from and
		including C{self}).

		:param block_type: If not ``None``, yield only blocks of the type C{block_type}.
		:param follow_all: If C{block_type} is not ``None``, then if this is ``True`` the function will parse the whole tree. Otherwise, the function will not follow branches that start by a non-C{block_type} block.

		:param unique: Whether the generator can return the same block twice or not."""
		# unique blocks: reduce this to the case of non-unique blocks
		if unique:
			block_list = []
			for block in self.tree(block_type = block_type, follow_all = follow_all, unique = False):
				if not block in block_list:
					yield block
					block_list.append(block)
			return

		# yield self
		if not block_type:
			yield self
		elif isinstance(self, block_type):
			yield self
		elif not follow_all:
			return # don't recurse further

		# yield tree attached to each child
		for child in type(self).get_refs(self):
			yield from child.tree(block_type=block_type, follow_all=follow_all)

	def get_hash(self):
        # conversion of the original pyffi get_hash function which was a method on every class
		def get_struct_hash(struct_type, struct_instance, args=()):
			hsh = []
			for f_name, f_type, f_args, _ in struct_type._get_filtered_attribute_list(struct_instance, *args[3:4]):
				field_value = struct_type.get_field(struct_instance, f_name)
				if issubclass(f_type, (BaseEnum, BasicBitfield)):
					# these can be converted to ints
					f_hash = int(field_value)
				elif issubclass(f_type, Ref):
					# a ref is none or points to a NiObject
					if field_value is None:
						f_hash = field_value
					else:
						f_hash = field_value.get_hash()
				elif issubclass(f_type, Ptr):
					# can't use get_hash on the niobject in the pointer to prevent infinite recursion
					f_hash = None
				elif callable(getattr(f_type, "_get_filtered_attribute_list", None)):
					f_hash = get_struct_hash(f_type, field_value, f_args)
				else:
					# assume it is a basic-like, i.e. immutable objects like numbers or strings
					f_hash = field_value
				hsh.append((f_name, f_hash))
			return tuple(hsh)
		return get_struct_hash(type(self), self)

	def _validateTree(self):
		"""Raises ValueError if there is a cycle in the tree."""
		# If the tree is parsed, then each block should be visited once.
		# However, as soon as some cycle is present, parsing the tree
		# will visit some child more than once (and as a consequence, infinitely
		# many times). So, walk the reference tree and check that every block is
		# only visited once.
		children = []
		for child in self.tree():
			if child in children:
				raise ValueError('cyclic references detected')
			children.append(child)

	def is_interchangeable(self, other):
		"""Are the two blocks interchangeable?

		@todo: Rely on AnyType, SimpleType, ComplexType, etc. implementation.
		"""
		if isinstance(self, (NifFormat.classes.NiProperty, NifFormat.classes.NiSourceTexture)):
			# use hash for properties and source textures
			return ((self.__class__ is other.__class__)
					and (self.get_hash() == other.get_hash()))
		else:
			# for blocks with references: quick check only
			return self is other

	# GlobalNode

	def get_global_child_nodes(self, edge_filter=()):
		yield from self.get_refs()

	def get_global_display(self, edge_filter=()):
		"""Construct a convenient name for the block itself."""
		return (self.name if hasattr(self, "name") else "")

