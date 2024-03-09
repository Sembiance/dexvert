from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiTimeController import NiTimeController


class BSProceduralLightningController(NiTimeController):

	"""
	Skyrim, Paired with dummy TriShapes, this controller generates lightning shapes for special effects.
	First interpolator controls Generation.
	"""

	__name__ = 'BSProceduralLightningController'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# References generation interpolator.
		self.interpolator_1_generation = name_type_map['Ref'](self.context, 0, name_type_map['NiInterpolator'])

		# References interpolator for Mutation of strips
		self.interpolator_2_mutation = name_type_map['Ref'](self.context, 0, name_type_map['NiInterpolator'])

		# References subdivision interpolator.
		self.interpolator_3_subdivision = name_type_map['Ref'](self.context, 0, name_type_map['NiInterpolator'])

		# References branches interpolator.
		self.interpolator_4_num_branches = name_type_map['Ref'](self.context, 0, name_type_map['NiInterpolator'])

		# References branches variation interpolator.
		self.interpolator_5_num_branches_var = name_type_map['Ref'](self.context, 0, name_type_map['NiInterpolator'])

		# References length interpolator.
		self.interpolator_6_length = name_type_map['Ref'](self.context, 0, name_type_map['NiInterpolator'])

		# References length variation interpolator.
		self.interpolator_7_length_var = name_type_map['Ref'](self.context, 0, name_type_map['NiInterpolator'])

		# References width interpolator.
		self.interpolator_8_width = name_type_map['Ref'](self.context, 0, name_type_map['NiInterpolator'])

		# References interpolator for amplitude control. 0=straight, 50=wide
		self.interpolator_9_arc_offset = name_type_map['Ref'](self.context, 0, name_type_map['NiInterpolator'])
		self.subdivisions = name_type_map['Ushort'].from_value(6)
		self.num_branches = name_type_map['Ushort'].from_value(1)
		self.num_branches_variation = name_type_map['Ushort'].from_value(1)

		# How far lightning will stretch to.
		self.length = name_type_map['Float'].from_value(512.0)

		# How far lightning variation will stretch to.
		self.length_variation = name_type_map['Float'].from_value(30.0)

		# How wide the bolt will be.
		self.width = name_type_map['Float'].from_value(16.0)

		# Influences forking behavior with a multiplier.
		self.child_width_mult = name_type_map['Float'].from_value(0.75)
		self.arc_offset = name_type_map['Float'].from_value(20.0)
		self.fade_main_bolt = name_type_map['Bool'].from_value(True)
		self.fade_child_bolts = name_type_map['Bool'].from_value(True)
		self.animate_arc_offset = name_type_map['Bool'].from_value(True)

		# Reference to a shader property.
		self.shader_property = name_type_map['Ref'](self.context, 0, name_type_map['BSShaderProperty'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'interpolator_1_generation', name_type_map['Ref'], (0, name_type_map['NiInterpolator']), (False, None), (None, None)
		yield 'interpolator_2_mutation', name_type_map['Ref'], (0, name_type_map['NiInterpolator']), (False, None), (None, None)
		yield 'interpolator_3_subdivision', name_type_map['Ref'], (0, name_type_map['NiInterpolator']), (False, None), (None, None)
		yield 'interpolator_4_num_branches', name_type_map['Ref'], (0, name_type_map['NiInterpolator']), (False, None), (None, None)
		yield 'interpolator_5_num_branches_var', name_type_map['Ref'], (0, name_type_map['NiInterpolator']), (False, None), (None, None)
		yield 'interpolator_6_length', name_type_map['Ref'], (0, name_type_map['NiInterpolator']), (False, None), (None, None)
		yield 'interpolator_7_length_var', name_type_map['Ref'], (0, name_type_map['NiInterpolator']), (False, None), (None, None)
		yield 'interpolator_8_width', name_type_map['Ref'], (0, name_type_map['NiInterpolator']), (False, None), (None, None)
		yield 'interpolator_9_arc_offset', name_type_map['Ref'], (0, name_type_map['NiInterpolator']), (False, None), (None, None)
		yield 'subdivisions', name_type_map['Ushort'], (0, None), (False, 6), (None, None)
		yield 'num_branches', name_type_map['Ushort'], (0, None), (False, 1), (None, None)
		yield 'num_branches_variation', name_type_map['Ushort'], (0, None), (False, 1), (None, None)
		yield 'length', name_type_map['Float'], (0, None), (False, 512.0), (None, None)
		yield 'length_variation', name_type_map['Float'], (0, None), (False, 30.0), (None, None)
		yield 'width', name_type_map['Float'], (0, None), (False, 16.0), (None, None)
		yield 'child_width_mult', name_type_map['Float'], (0, None), (False, 0.75), (None, None)
		yield 'arc_offset', name_type_map['Float'], (0, None), (False, 20.0), (None, None)
		yield 'fade_main_bolt', name_type_map['Bool'], (0, None), (False, True), (None, None)
		yield 'fade_child_bolts', name_type_map['Bool'], (0, None), (False, True), (None, None)
		yield 'animate_arc_offset', name_type_map['Bool'], (0, None), (False, True), (None, None)
		yield 'shader_property', name_type_map['Ref'], (0, name_type_map['BSShaderProperty']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'interpolator_1_generation', name_type_map['Ref'], (0, name_type_map['NiInterpolator']), (False, None)
		yield 'interpolator_2_mutation', name_type_map['Ref'], (0, name_type_map['NiInterpolator']), (False, None)
		yield 'interpolator_3_subdivision', name_type_map['Ref'], (0, name_type_map['NiInterpolator']), (False, None)
		yield 'interpolator_4_num_branches', name_type_map['Ref'], (0, name_type_map['NiInterpolator']), (False, None)
		yield 'interpolator_5_num_branches_var', name_type_map['Ref'], (0, name_type_map['NiInterpolator']), (False, None)
		yield 'interpolator_6_length', name_type_map['Ref'], (0, name_type_map['NiInterpolator']), (False, None)
		yield 'interpolator_7_length_var', name_type_map['Ref'], (0, name_type_map['NiInterpolator']), (False, None)
		yield 'interpolator_8_width', name_type_map['Ref'], (0, name_type_map['NiInterpolator']), (False, None)
		yield 'interpolator_9_arc_offset', name_type_map['Ref'], (0, name_type_map['NiInterpolator']), (False, None)
		yield 'subdivisions', name_type_map['Ushort'], (0, None), (False, 6)
		yield 'num_branches', name_type_map['Ushort'], (0, None), (False, 1)
		yield 'num_branches_variation', name_type_map['Ushort'], (0, None), (False, 1)
		yield 'length', name_type_map['Float'], (0, None), (False, 512.0)
		yield 'length_variation', name_type_map['Float'], (0, None), (False, 30.0)
		yield 'width', name_type_map['Float'], (0, None), (False, 16.0)
		yield 'child_width_mult', name_type_map['Float'], (0, None), (False, 0.75)
		yield 'arc_offset', name_type_map['Float'], (0, None), (False, 20.0)
		yield 'fade_main_bolt', name_type_map['Bool'], (0, None), (False, True)
		yield 'fade_child_bolts', name_type_map['Bool'], (0, None), (False, True)
		yield 'animate_arc_offset', name_type_map['Bool'], (0, None), (False, True)
		yield 'shader_property', name_type_map['Ref'], (0, name_type_map['BSShaderProperty']), (False, None)
