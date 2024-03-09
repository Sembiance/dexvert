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
	'Bool': 'nifgen.formats.ovl_base.basic',
	'OffsetString': 'nifgen.formats.ovl_base.basic',
	'Compression': 'nifgen.formats.ovl_base.enums.Compression',
	'VersionInfo': 'nifgen.formats.ovl_base.bitfields.VersionInfo',
	'Pointer': 'nifgen.formats.ovl_base.compounds.Pointer',
	'Reference': 'nifgen.formats.ovl_base.compounds.Reference',
	'LookupPointer': 'nifgen.formats.ovl_base.compounds.LookupPointer',
	'ArrayPointer': 'nifgen.formats.ovl_base.compounds.ArrayPointer',
	'CondPointer': 'nifgen.formats.ovl_base.compounds.CondPointer',
	'ForEachPointer': 'nifgen.formats.ovl_base.compounds.ForEachPointer',
	'MemStruct': 'nifgen.formats.ovl_base.compounds.MemStruct',
	'SmartPadding': 'nifgen.formats.ovl_base.compounds.SmartPadding',
	'ZStringObfuscated': 'nifgen.formats.ovl_base.basic',
	'GenericHeader': 'nifgen.formats.ovl_base.compounds.GenericHeader',
	'Empty': 'nifgen.formats.ovl_base.compounds.Empty',
	'ZStringList': 'nifgen.formats.ovl_base.compounds.ZStringList',
	'ResearchRoot': 'nifgen.formats.animalresearch.compounds.ResearchRoot',
	'ResearchLevel': 'nifgen.formats.animalresearch.compounds.ResearchLevel',
	'UnlockState': 'nifgen.formats.animalresearch.compounds.UnlockState',
	'ResearchStartRoot': 'nifgen.formats.animalresearch.compounds.ResearchStartRoot',
}

name_type_map = {}
for type_name, module in type_module_name_map.items():
	name_type_map[type_name] = getattr(import_module(module), type_name)
for class_object in name_type_map.values():
	if callable(getattr(class_object, 'init_attributes', None)):
		class_object.init_attributes()
