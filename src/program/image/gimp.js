import {xu} from "xu";
import {path} from "std";
import {fileUtil} from "xutil";
import {Program} from "../../Program.js";

export class gimp extends Program
{
	website = "https://gimp.org";
	package = "media-gfx/gimp";
	bin     = "gimp";

	pre = async r =>
	{
		// DOCUMENTATION: Open gimp and go to Help->Procedure Browser
		// In there you can look at the various procedures that GIMP has available along with which named arguments to pass and their types
		// An up to date example of the latest python code is: file:///usr/lib64/gimp/2.99/plug-ins/file-openraster/file-openraster.py
		await fileUtil.writeTextFile(path.join(r.f.root, "dexvert.py"), `import gi
from gi.repository import GObject, Gimp, Gio

def loadAndSave(inPath, outPath):
	pdb = Gimp.get_pdb()

	loadProc = pdb.lookup_procedure("gimp-file-load")
	loadConfig = loadProc.create_config()
	loadConfig.set_property("run-mode", Gimp.RunMode.NONINTERACTIVE)
	loadConfig.set_property("file", Gio.File.new_for_path(inPath))
	image = loadProc.run(loadConfig).index(1)

	if type(image) is Gimp.Image:
		saveProc = pdb.lookup_procedure("file-png-export")
		saveConfig = saveProc.create_config()
		saveConfig.set_property("run-mode", Gimp.RunMode.NONINTERACTIVE)
		saveConfig.set_property("image", image)
		saveConfig.set_property("file", Gio.File.new_for_path(outPath))
		saveConfig.set_property("interlaced", False)
		saveConfig.set_property("compression", 9)
		saveConfig.set_property("bkgd", False)
		saveConfig.set_property("offs", False)
		saveConfig.set_property("phys", False)
		saveConfig.set_property("time", False)
		saveConfig.set_property("save-transparent", False)
		saveConfig.set_property("optimize-palette", False)
		saveProc.run(saveConfig)

	quitProc = pdb.lookup_procedure("gimp-quit")
	quitConfig = quitProc.create_config()
	quitConfig.set_property("force", True)
	quitProc.run(quitConfig)`);
	};

	args       = async r => ["-ni", "--batch-interpreter", "python-fu-eval", "-b", `import sys;sys.path=['.']+sys.path;import dexvert;dexvert.loadAndSave('${r.inFile()}', '${await r.outFile("out.png")}')`];
	runOptions = ({timeout : xu.MINUTE*2, virtualX : true});
	renameOut  = true;
}
