from nifgen.array import Array
from nifgen.base_struct import BaseStruct
from nifgen.formats.base.basic import Float
import numpy as np

from nifgen.base_struct import BaseStruct


class FloatsGrabber(BaseStruct):

	__name__ = 'FloatsGrabber'


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

	@classmethod
	def read_fields(cls, stream, instance):
		instance.io_start = stream.tell()
		num_bounds = np.max(instance.arg) + 1
		instance.mins = Array.from_stream(stream, instance.context, 0, None, (num_bounds, 3), Float)
		instance.scales = Array.from_stream(stream, instance.context, 0, None, (num_bounds, 3), Float)
		instance.io_size = stream.tell() - instance.io_start

	@classmethod
	def write_fields(cls, stream, instance):
		instance.io_start = stream.tell()
		Array.to_stream(instance.mins, stream, instance.context, 0, None, instance.mins.shape, Float)
		Array.to_stream(instance.scales, stream, instance.context, 0, None, instance.scales.shape, Float)
		instance.io_size = stream.tell() - instance.io_start

	@classmethod
	def get_fields_str(cls, instance, indent=0):
		return f"\nMins:\n{instance.mins}, \nScales:\n{instance.scales}"


