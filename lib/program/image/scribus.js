"use strict";
const XU = require("@sembiance/xu"),
	fs = require("fs"),
	path = require("path");

exports.meta =
{
	website        : "https://www.scribus.net/",
	gentooPackage  : "app-office/scribus",
	gentooUseFlags : "boost minimal pdf templates",
	bruteUnsafe    : true
};

exports.bin = () => "scribus";
exports.args = (state, p, r, inPath="conv.py") => (["--prefs", path.join(__dirname, "..", "..", "..", "scribus"), "-ns", "-py", inPath]);

// SCRIPT API: https://wiki.scribus.net/canvas/Automatic_Scripter_Commands_list

// Right now we only support converting to SVG. In the future I should add a state.scribusFormat and optionally convert to PDF for documents
exports.pre = (state, p, r, cb) =>
{
	// So I used to iterate over all the objects, measure width/height and x/y of every object, figuring out how big the canvas needed to be exactly
	// I later simplified that to just a getSize(groupObjects(getAllObjects()))
	// Sadly some files have objects that don't seem to register with the API getAllObjects() and thus some of the image was always cut off
	// So now I just make a really big document and then inkscape will crop that using the 'export-area-drawing flag. Works.
	fs.writeFile(path.join(state.cwd, "conv.py"), `from scribus import *
import scribus

scribus.newDocument((50000, 50000), (0, 0, 0, 0), scribus.PORTRAIT, 1, scribus.UNIT_POINTS, scribus.PAGE_1, 0, 1)
scribus.setUnit(scribus.UNIT_POINTS)
scribus.placeVectorFile("${path.basename(state.input.filePath)}", 0, 0)
scribus.savePageAsEPS("outfile.eps")
scribus.closeDoc()
scribus.fileQuit()
`, XU.UTF8, cb);
};

exports.post = (state, p, r, cb) => p.util.program.run("inkscape", {argsd : ["outfile.eps"]})(state, p, cb);

exports.runOptions = () => ({timeout : XU.MINUTE, virtualX : true, killSignal : "SIGTERM"});	// scribus won't kill with SIGINT
