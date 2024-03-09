from importlib import import_module


type_module_name_map = {
	'Biguint32': 'nifgen.formats.psi.basic',
	'Bigushort': 'nifgen.formats.psi.basic',
	'Ubyte': 'nifgen.formats.psi.basic',
	'Char': 'nifgen.formats.psi.basic',
	'LineString': 'nifgen.formats.psi.basic',
	'FixedString': 'nifgen.formats.psi.structs.FixedString',
	'SizedString': 'nifgen.formats.psi.structs.SizedString',
	'PhonemeRecord': 'nifgen.formats.psi.structs.PhonemeRecord',
	'SimilarPhonemeRecord': 'nifgen.formats.psi.structs.SimilarPhonemeRecord',
	'UnknownStruct': 'nifgen.formats.psi.structs.UnknownStruct',
	'Header': 'nifgen.formats.psi.structs.Header',
}

name_type_map = {}
for type_name, module in type_module_name_map.items():
	name_type_map[type_name] = getattr(import_module(module), type_name)
for class_object in name_type_map.values():
	if callable(getattr(class_object, 'init_attributes', None)):
		class_object.init_attributes()
