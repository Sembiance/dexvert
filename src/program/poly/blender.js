import {xu} from "xu";
import {Program} from "../../Program.js";
import {fileUtil} from "xutil";
import {path} from "std";

const _VALID_FORMATS =
{
	// Almost every addon in this list I've modified to fix bugs or ignore errors
	"3ds"   : {importKey : "import_scene.max3ds", addon : "io_scene_3ds"},			// blender comes with this addon
	ac3d    : {importKey : "import_scene.import_ac3d", addon : "io_scene_ac3d"},	// https://github.com/NikolaiVChr/Blender-AC3D/tree/4.0
	b3d     : {importKey : "import_scene.blitz3d_b3d", addon : "io_scene_b3d"},		// https://github.com/joric/io_scene_b3d
	dxf     : {importKey : "import_scene.dxf", addon : "io_import_dxf"},			// blender comes with this addon
	lwo     : {importKey : "import_scene.lwo", addon : "io_scene_lwo"},				// https://github.com/nangtani/blender-import-lwo
	md2     : {importKey : "import_md2.some_data", addon : "io_import_md2"},		// https://github.com/lennart-g/blender-md2-importer
	//md3     : {importKey : "import_scene.md3", addon : "io_scene_md3"},			// https://github.com/hypov8/blender-md3_2.7-3.2		(Couldn't get it to work)
	md5mesh : {importKey : "import_scene.md5mesh", addon : "io_scene_md5_28"},		// https://github.com/KozGit/Blender-2.8-MD5-import-export-addon
	ms3d    : {importKey : "import_scene.ms3d", addon : "io_scene_ms3d"},			// used to be built into blender in the past, now I grabbed it from: https://projects.blender.org/blender/blender-addons/issues/98826
	nif     : {importKey : "import_scene.nif", addon : "io_scene_niftools"},		// https://github.com/niftools/blender_niftools_addon
	smd     : {importKey : "import_scene.smd", addon : "io_scene_valvesource"},		// https://github.com/Artfunkel/BlenderSourceTools
	tddd    : {importKey : "import_scene.tddd", addon : "io_import_scene_tddd"},	// https://github.com/wizardgsz/Imagine-T3D-Importer
	x       : {importKey : "import_scene.x", addon : "Blender-XFileImporter"},		// https://github.com/oguna/Blender-XFileImporter
	x3d     : {importKey : "import_scene.x3d", addon : "io_scene_x3d"},				// blender comes with this addong
	
	// built into blender natively
	collada : {},
	obj     : {},
	ply     : {},
	stl     : {}
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

			${r.flags.format!=="native" ? `
			${_VALID_FORMATS[r.flags.format].addon ? `bpy.ops.preferences.addon_enable(module="${_VALID_FORMATS[r.flags.format].addon}")` : ""}
			#print(dir(bpy.ops.import_scene))
			${_VALID_FORMATS[r.flags.format].importKey ? `bpy.ops.${_VALID_FORMATS[r.flags.format].importKey}(filepath=sys.argv[5])` : `bpy.ops.wm.${r.flags.format}_import(filepath=sys.argv[5])`}
			
			bpy.ops.wm.save_as_mainfile(filepath=sys.argv[6])
			bpy.ops.wm.window_close()` : ""}

			bpy.ops.wm.open_mainfile(filepath=sys.argv[${r.flags.format==="native" ? "5" : "6"}])
			bpy.ops.export_scene.gltf(filepath=sys.argv[7])`.trim().split("\n").map(l => l.trim()).join("\n"));
	};
	
	args       = async r => ["--background", "--python", r.blenderScriptPath, "--", r.inFile({absolute : true}), r.tempBlendPath, await r.outFile("out.glb", {absolute : true})];
	runOptions = ({timeout : xu.MINUTE, env : {BLENDER_USER_SCRIPTS : path.join(import.meta.dirname, "..", "..", "..", "blender")}});
	renameOut  = true;
}
