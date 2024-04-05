import {xu} from "xu";
import {Program} from "../../Program.js";
import {fileUtil} from "xutil";
import {path} from "std";

const SCRIBUS_PREF_FILENAMES = [".neversplash", "checkfonts150.xml", "prefs150.xml", "scribus150.rc", "scribusshapes.xml"];
const SCRIBUS_PREF_SRC = path.join(import.meta.dirname, "../../../scribus");

export class scribus extends Program
{
	website = "https://www.scribus.net/";
	package = "app-office/scribus";
	unsafe  = true;
	bin     = "scribus-1.6";
	outExt  = ".eps";

	pre = async r =>
	{
		// scribus requires certain files to properly convert, but it also modifies these files when we run scribus
		// to be extra careful, whenever we run scribus we will create a temporary with fresh copies of these files
		r.scribusDirPath = await fileUtil.genTempPath(r.f.root, "scribus");

		await Deno.mkdir(r.scribusDirPath, {recursive : true});
		for(const filename of SCRIBUS_PREF_FILENAMES)
			await Deno.copyFile(path.join(SCRIBUS_PREF_SRC, filename), path.join(r.scribusDirPath, filename));
		
		// now we create a conv.py pythong script to convert to SVG
		// right now it only supports converting to EPS (then to PNG+SVG). In the future I could add a flag to optionally convert to PDF for documents
		// SCRIPT API: https://wiki.scribus.net/canvas/Automatic_Scripter_Commands_list

		// So I used to iterate over all the objects, measure width/height and x/y of every object, figuring out how big the canvas needed to be exactly
		// I later simplified that to just a getSize(groupObjects(getAllObjects()))
		// Sadly some files have objects that don't seem to register with the API getAllObjects() and thus some of the image was always cut off
		// So now I just make a really big document and then inkscape will crop that using the 'export-area-drawing flag. Works.
		await fileUtil.writeTextFile(path.join(r.scribusDirPath, "conv.py"), `from scribus import *
import scribus

scribus.newDocument((50000, 50000), (0, 0, 0, 0), scribus.PORTRAIT, 1, scribus.UNIT_POINTS, scribus.PAGE_1, 0, 1)
scribus.setUnit(scribus.UNIT_POINTS)
scribus.placeVectorFile("${r.inFile()}", 0, 0)
scribus.savePageAsEPS("${await r.outFile("out.eps")}")
scribus.closeDoc()
scribus.fileQuit()`);
	};

	args       = r => ["--prefs", r.scribusDirPath, "-ns", "-py", path.join(path.basename(r.scribusDirPath), "conv.py"), r.inFile()];
	runOptions = ({timeout : xu.MINUTE, virtualX : true});
	renameOut  = true;
	chain      = "inkscape";	// if I also wanted .png output, I could change inkscape to: dexvert[asFormat:image/eps]
}
