import {Program} from "../../Program.js";
import {fileUtil} from "xutil";
import {path} from "std";

const _VALID_FORMATS =
{
	tddd    : "io_import_scene_tddd",	// https://github.com/wizardgsz/Imagine-T3D-Importer				(modified by me to fix some bugs with some files)
	nif     : "io_scene_niftools",		// https://github.com/niftools/blender_niftools_addon				(modified by me to fix some bugs with some files)
	smd     : "io_scene_valvesource",	// https://github.com/Artfunkel/BlenderSourceTools
	md5mesh : "io_scene_md5_28",		// https://github.com/KozGit/Blender-2.8-MD5-import-export-addon	(modified by me to fix some bugs with some files)
	
	// built into blender
	collada : null,
	obj     : null,
	stl     : null
};

export class blender extends Program
{
	website   = "https://www.blender.org";
	package   = "media-gfx/blender";
	bin       = "blender-4.0";
	flags   = {
		format      : "Specify which format to import. REQUIRED"
	};

	// API: https://docs.blender.org/api/current/bpy.ops.wm.html
	pre = async r =>
	{
		r.blenderScriptPath = await fileUtil.genTempPath(r.f.root, ".py");
		r.tempBlendPath = await fileUtil.genTempPath(r.f.root, ".blend");

		await fileUtil.writeTextFile(r.blenderScriptPath, `
			import bpy
			import sys

			bpy.ops.wm.read_factory_settings(use_empty=True)

			${_VALID_FORMATS[r.flags.format]===null ? `bpy.ops.wm.${r.flags.format}_import(filepath=sys.argv[5])` : `
			bpy.ops.preferences.addon_enable(module="${_VALID_FORMATS[r.flags.format]}")
			bpy.ops.import_scene.${r.flags.format}(filepath=sys.argv[5])`}

			bpy.ops.wm.save_as_mainfile(filepath=sys.argv[6])

			bpy.ops.wm.window_close()
			bpy.ops.wm.open_mainfile(filepath=sys.argv[6])
			bpy.ops.export_scene.gltf(filepath=sys.argv[7])`.trim().split("\n").map(l => l.trim()).join("\n"));
	};
	
	args       = async r => ["--background", "--python", r.blenderScriptPath, "--", r.inFile({absolute : true}), r.tempBlendPath, await r.outFile("out.glb", {absolute : true})];
	runOptions = ({env : {BLENDER_USER_SCRIPTS : path.join(import.meta.dirname, "..", "..", "..", "blender")}});
	renameOut  = true;
}
