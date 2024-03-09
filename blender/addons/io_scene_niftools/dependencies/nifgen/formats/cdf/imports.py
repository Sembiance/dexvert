from importlib import import_module


type_module_name_map = {
	'Ubyte': 'nifgen.formats.cdf.basic',
	'Char': 'nifgen.formats.cdf.basic',
	'Littleuint32': 'nifgen.formats.cdf.basic',
	'FixedString': 'nifgen.formats.cdf.structs.FixedString',
	'ExportString': 'nifgen.formats.cdf.structs.ExportString',
	'SizedString': 'nifgen.formats.cdf.structs.SizedString',
	'FileObject': 'nifgen.formats.cdf.structs.FileObject',
	'Header': 'nifgen.formats.cdf.structs.Header',
}

name_type_map = {}
for type_name, module in type_module_name_map.items():
	name_type_map[type_name] = getattr(import_module(module), type_name)
for class_object in name_type_map.values():
	if callable(getattr(class_object, 'init_attributes', None)):
		class_object.init_attributes()
