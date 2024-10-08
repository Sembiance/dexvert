from importlib import import_module


type_module_name_map = {
	'Byte': 'nifgen.formats.base.basic',
	'Ubyte': 'nifgen.formats.base.basic',
	'Uint64': 'nifgen.formats.base.basic',
	'Int64': 'nifgen.formats.base.basic',
	'Uint': 'nifgen.formats.base.basic',
	'Ushort': 'nifgen.formats.base.basic',
	'Int': 'nifgen.formats.base.basic',
	'Short': 'nifgen.formats.base.basic',
	'Char': 'nifgen.formats.base.basic',
	'Normshort': 'nifgen.formats.base.basic',
	'Rangeshort': 'nifgen.formats.base.basic',
	'Float': 'nifgen.formats.base.basic',
	'Double': 'nifgen.formats.base.basic',
	'Hfloat': 'nifgen.formats.base.basic',
	'ZString': 'nifgen.formats.base.basic',
	'ZStringBuffer': 'nifgen.formats.base.compounds.ZStringBuffer',
	'PadAlign': 'nifgen.formats.base.compounds.PadAlign',
	'FixedString': 'nifgen.formats.base.compounds.FixedString',
	'Vector2': 'nifgen.formats.base.compounds.Vector2',
	'Vector3': 'nifgen.formats.base.compounds.Vector3',
	'Vector4': 'nifgen.formats.base.compounds.Vector4',
	'FourCC': 'nifgen.formats.dds.enums.FourCC',
	'DxgiFormat': 'nifgen.formats.dds.enums.DxgiFormat',
	'D3D10ResourceDimension': 'nifgen.formats.dds.enums.D3D10ResourceDimension',
	'HeaderFlags': 'nifgen.formats.dds.bitstructs.HeaderFlags',
	'PixelFormatFlags': 'nifgen.formats.dds.bitstructs.PixelFormatFlags',
	'Caps1': 'nifgen.formats.dds.bitstructs.Caps1',
	'Caps2': 'nifgen.formats.dds.bitstructs.Caps2',
	'PixelFormat': 'nifgen.formats.dds.structs.PixelFormat',
	'Dxt10Header': 'nifgen.formats.dds.structs.Dxt10Header',
	'Header': 'nifgen.formats.dds.structs.Header',
}

name_type_map = {}
for type_name, module in type_module_name_map.items():
	name_type_map[type_name] = getattr(import_module(module), type_name)
for class_object in name_type_map.values():
	if callable(getattr(class_object, 'init_attributes', None)):
		class_object.init_attributes()
