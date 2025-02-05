#!/usr/bin/env python3
import glob, json, importlib.util, sys, os

def loadPluginMeta(pluginPath):
	spec = importlib.util.spec_from_file_location("plugin", pluginPath)
	mod = importlib.util.module_from_spec(spec)
	spec.loader.exec_module(mod)
	formats = getattr(mod, "FORMATS_FILES", None)
	if formats is None:
		formats = getattr(mod, "FORMATS_ARCHIVE", [])
	types = getattr(mod, "TYPES_FILES", None)
	if types is None:
		types = getattr(mod, "TYPES_ARCHIVE", [])
	fname = os.path.splitext(os.path.basename(pluginPath))[0]
	if fname.startswith("g_"):
		fname = fname[2:]
	return {
		"NAME": getattr(mod, "NAME", "N/A"),
		"filename": fname,
		"GAMES": getattr(mod, "GAMES", []),
		"FORMATS": formats,
		"TYPES": types,
		"AUTHOR": getattr(mod, "AUTHOR", "N/A")
	}

def main():
	metaList = []
	for pluginPath in glob.glob("plugins/*.py"):
		try:
			metaList.append(loadPluginMeta(pluginPath))
		except Exception as e:
			print(f"Error loading {pluginPath}: {e}", file=sys.stderr)
	with open("meta.json", "w", encoding="utf-8") as f:
		json.dump(metaList, f, ensure_ascii=False, separators=(',', ':'))

if __name__ == "__main__":
	main()