import {xu} from "xu";
import {path} from "std";
import {fileUtil} from "xutil";
import {Program} from "../../Program.js";

export class gimp extends Program
{
	website = "https://gimp.org";
	package = "media-gfx/gimp";

	// NOTE: I snapshotted gimp-2.99.10-r1 on Sep 2022 because later versions broke python plugin support
	bin = "/usr/bin/gimp";	// Full path to ensure the python enabled gimp version is used instead of the appimage one

	pre = async r =>
	{
		// big thanks to this GIST for teaching me python 3 syntax for GIMP: https://github.com/nicolalandro/u2net_gimp_plugin/blob/639fd6cb7bed3d7b920c0b0666fcda3c3506e2d4/u2net_gimp_plugin.py
		// I could recode the below with JavaScript if I so chose: https://gitlab.gnome.org/GNOME/gimp/-/blob/master/extensions/goat-exercises/goat-exercise-gjs.js
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
            GObject.Value(
                Gio.File,
                Gio.File.new_for_path(inPath),
            )
        ]
    ).index(1)

	if type(image) is Gimp.Image:
		drawable = image.get_active_layer()

		pdb.run_procedure(
			"file-png-save",
			[
				GObject.Value(Gimp.RunMode, Gimp.RunMode.NONINTERACTIVE),
				GObject.Value(Gimp.Image, image),
				GObject.Value(GObject.TYPE_INT, 1),
				GObject.Value(
					Gimp.ObjectArray, Gimp.ObjectArray.new(Gimp.Drawable, [drawable], 0)
				),
				GObject.Value(
					Gio.File,
					Gio.File.new_for_path(outPath),
				),
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
