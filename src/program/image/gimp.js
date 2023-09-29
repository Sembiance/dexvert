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
		// Originally I used this GIST for teaching me python 3 syntax for GIMP: https://github.com/nicolalandro/u2net_gimp_plugin/blob/639fd6cb7bed3d7b920c0b0666fcda3c3506e2d4/u2net_gimp_plugin.py
		// But that GIST is now OUT OF DATE and does not work. I fixed it by examining: https://github.com/GNOME/gimp/blob/196f1d6e9534938d9aa15881857cef56dc721ec6/plug-ins/python/file-openraster.py#L413
		// I could recode the below with JavaScript if I so chose: https://gitlab.gnome.org/GNOME/gimp/-/blob/master/extensions/goat-exercises/goat-exercise-gjs.js
		// NOTE: GIMP isn't currently being compiled with JavaScript support so...
		await fileUtil.writeTextFile(path.join(r.f.root, "dexvert.py"), `import gi
from gi.repository import GObject
from gi.repository import Gimp
from gi.repository import Gio

def loadAndSave(inPath, outPath):
	pdb = Gimp.get_pdb()

	image = pdb.run_procedure(
        "gimp-file-load",
        [
            GObject.Value(Gimp.RunMode, Gimp.RunMode.NONINTERACTIVE),
            GObject.Value(Gio.File, Gio.File.new_for_path(inPath))
        ]
    ).index(1)

	if type(image) is Gimp.Image:
		drawable = pdb.run_procedure(
			"gimp-file-load-layer",
			[
				GObject.Value(Gimp.RunMode, Gimp.RunMode.NONINTERACTIVE),
				GObject.Value(Gimp.Image, image),
				GObject.Value( Gio.File, Gio.File.new_for_path(inPath))
			]
		).index(1)

		if type(drawable) is Gimp.Layer:
			pdb.run_procedure(
				"file-png-save",
				[
					GObject.Value(Gimp.RunMode, Gimp.RunMode.NONINTERACTIVE),
					GObject.Value(Gimp.Image, image),
					GObject.Value(GObject.TYPE_INT, 1),
					GObject.Value(Gimp.ObjectArray, Gimp.ObjectArray.new(Gimp.Drawable, [drawable], 0)),
					GObject.Value(Gio.File, Gio.File.new_for_path(outPath)),
					GObject.Value(GObject.TYPE_BOOLEAN, 0),
					GObject.Value(GObject.TYPE_INT, 9),

					GObject.Value(GObject.TYPE_BOOLEAN, False),
					GObject.Value(GObject.TYPE_BOOLEAN, False),
					GObject.Value(GObject.TYPE_BOOLEAN, False),
					GObject.Value(GObject.TYPE_BOOLEAN, False)
				]
			)

		pdb.run_procedure(
			"gimp-quit",
			[
				GObject.Value(GObject.TYPE_BOOLEAN, True)
			]
		)`);
	};

	args       = async r => ["-ni", "--batch-interpreter", "python-fu-eval", "-b", `import sys;sys.path=['.']+sys.path;import dexvert;dexvert.loadAndSave('${r.inFile()}', '${await r.outFile("out.png")}')`];
	runOptions = ({timeout : xu.MINUTE*2, virtualX : true});
	renameOut  = true;
}
