import {xu} from "xu";
import {Program} from "../../Program.js";
import {fileUtil} from "xutil";
import {path} from "std";

const SCRIBUS_PREF_FILENAMES = [".neversplash", "checkfonts170.xml", "prefs170.xml", "scribus170.rc", "scribusshapes.xml"];
const SCRIBUS_PREF_SRC = path.join(import.meta.dirname, "../../../scribus");

export class scribus extends Program
{
	website = "https://www.scribus.net/";
	package = "app-office/scribus";
	flags   = {
		outType : `Which format to output: svg | pdf. Default is svg`
	};
	unsafe = true;
	bin    = "scribus-1.7";
	outExt = r => ((r.flags.outType || "svg")==="pdf" ? ".pdf" : ".eps");

	pre = async r =>
	{
		// scribus requires certain files to properly convert, but it also modifies these files when we run scribus
		// to be extra careful, whenever we run scribus we will create a temporary with fresh copies of these files
		r.scribusDirPath = await fileUtil.genTempPath(r.f.root, "scribus");

		await Deno.mkdir(r.scribusDirPath, {recursive : true});
		for(const filename of SCRIBUS_PREF_FILENAMES)
			await Deno.copyFile(path.join(SCRIBUS_PREF_SRC, filename), path.join(r.scribusDirPath, filename));
		
		// SCRIPT API: https://wiki.scribus.net/canvas/Automatic_Scripter_Commands_list
		// 2026 Feb NOTE: May have a more recent API available: https://scribus-scripter.readthedocs.io/en/latest/#python-scripts     https://wiki.scribus.net/canvas/Scripter2_API

		// So I used to iterate over all the objects, measure width/height and x/y of every object, figuring out how big the canvas needed to be exactly
		// I later simplified that to just a getSize(groupObjects(getAllObjects()))
		// Sadly some files have objects that don't seem to register with the API getAllObjects() and thus some of the image was always cut off
		// So now I just make a really big document and then inkscape will crop that using the 'export-area-drawing flag. Works.
		await fileUtil.writeTextFile(path.join(r.scribusDirPath, "conv.py"), `from scribus import *
import scribus

${(r.flags.outType || "svg")==="pdf" ? `
scribus.openDoc("${r.inFile()}")
pdf = scribus.PDFfile()
pdf.file = "${await r.outFile("out.pdf")}"
pdf.save()
` : `
scribus.newDocument((50000, 50000), (0, 0, 0, 0), scribus.PORTRAIT, 1, scribus.UNIT_POINTS, scribus.PAGE_1, 0, 1)
scribus.setUnit(scribus.UNIT_POINTS)
scribus.placeVectorFile("${r.inFile()}", 0, 0)
scribus.savePageAsEPS("${await r.outFile("out.eps")}")
`}

scribus.closeDoc()
scribus.fileQuit()`);
	};

	args       = r => ["--no-gui", "--prefs", r.scribusDirPath, "-ns", "-py", path.join(path.basename(r.scribusDirPath), "conv.py"), r.inFile()];
	runOptions = ({timeout : xu.MINUTE, virtualX : true});	// scribus gets hung up on font substitution, presenting a dialog despire --no-gui. Could maybe add a scribusWin on win7 that uses autoit to do the conversion instead of linux headless as a backup
	renameOut  = true;
	chain      = "?inkscape";
	chainCheck = r => ((r.flags.outType || "svg")==="svg");
}
