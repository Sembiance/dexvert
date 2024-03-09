from nifgen.base_struct import BaseStruct

ZERO = b"\x00"

def get_padding_size(size, alignment=16):
	mod = size % alignment
	if mod:
		return alignment - mod
	return 0


def get_padding(size, alignment=16):
	if alignment:
		# create the new blank padding
		return ZERO * get_padding_size(size, alignment=alignment)
	return b""


from nifgen.base_struct import BaseStruct


class PadAlign(BaseStruct):

	"""
	Grabs as many bytes as needed to align #ARG# bytes from the start of #TEMPLATE#
	"""

	__name__ = 'PadAlign'


	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)

	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.data = b""

	def get_pad(self, stream):
		distance = stream.tell() - self.template.io_start
		return get_padding_size(distance, alignment=self.arg)

	def __repr__(self):
		return f"{self.data} Size: {len(self.data)}"

	@classmethod
	def read_fields(cls, stream, instance):
		instance.data = stream.read(instance.get_pad(stream))

	@classmethod
	def write_fields(cls, stream, instance):
		instance.data = ZERO * instance.get_pad(stream)
		stream.write(instance.data)

	@staticmethod
	def get_size(instance, context, arg=0, template=None):
		# this is actually somewhat indeterminate as there is no stream to work off, so work off the last known stream
		# position: instance.io_start
		return get_padding_size(instance.io_start - instance.template.io_start, alignment=instance.arg)

