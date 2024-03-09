from importlib import import_module


type_module_name_map = {
	'Biguint32': 'nifgen.formats.pdc.basic',
	'Bigushort': 'nifgen.formats.pdc.basic',
	'Ubyte': 'nifgen.formats.pdc.basic',
	'Char': 'nifgen.formats.pdc.basic',
	'LineString': 'nifgen.formats.pdc.basic',
	'FixedString': 'nifgen.formats.pdc.structs.FixedString',
	'SizedString': 'nifgen.formats.pdc.structs.SizedString',
	'CharacterEntry': 'nifgen.formats.pdc.structs.CharacterEntry',
	'G2Pb': 'nifgen.formats.pdc.structs.G2Pb',
	'Index7Bytes': 'nifgen.formats.pdc.structs.Index7Bytes',
	'UshortArrayContainer': 'nifgen.formats.pdc.structs.UshortArrayContainer',
	'WordEntry': 'nifgen.formats.pdc.structs.WordEntry',
	'PDCWordList': 'nifgen.formats.pdc.structs.PDCWordList',
	'PDCFile': 'nifgen.formats.pdc.structs.PDCFile',
}

name_type_map = {}
for type_name, module in type_module_name_map.items():
	name_type_map[type_name] = getattr(import_module(module), type_name)
for class_object in name_type_map.values():
	if callable(getattr(class_object, 'init_attributes', None)):
		class_object.init_attributes()
