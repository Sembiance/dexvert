import {xu} from "xu";
import {Program} from "../../Program.js";
import {fileUtil} from "xutil";
import * as path from "https://deno.land/std@0.114.0/path/mod.ts";

const SCRIBUS_PREF_FILENAMES = [".neversplash", "checkfonts150.xml", "prefs150.xml", "scribus150.rc", "scribusshapes.xml"];
const SCRIBUS_PREF_SRC = path.join(xu.dirname(import.meta), "../../../scribus");

export class scribus extends Program
{
	website        = "https://www.scribus.net/";
	gentooPackage  = "app-office/scribus";
	gentooUseFlags = "boost minimal pdf templates";
	unsafe         = true;

	bin = "scribus";
	outExt = () => ".eps";

	pre = async r =>
	{
		// scribus requires certain files to properly convert, but it also modifies these files when we run scribus
		// to be extra careful, whenever we run scribus we will create a temporary with fresh copies of these files
		r.scribusDirPath = await fileUtil.genTempPath(r.f.root, "scribus");

		await Deno.mkdir(r.scribusDirPath, {recursive : true});
		for(const filename of SCRIBUS_PREF_FILENAMES)
			await Deno.copyFile(path.join(SCRIBUS_PREF_SRC, filename), path.join(r.scribusDirPath, filename));
		
		// now we create a conv.py pythong script to convert to SVG
		// right now it only supports converting to SVG. In the future I could add a flag to optionally convert to PDF for documents
		// SCRIPT API: https://wiki.scribus.net/canvas/Automatic_Scripter_Commands_list

		// So I used to iterate over all the objects, measure width/height and x/y of every object, figuring out how big the canvas needed to be exactly
		// I later simplified that to just a getSize(groupObjects(getAllObjects()))
		// Sadly some files have objects that don't seem to register with the API getAllObjects() and thus some of the image was always cut off
		// So now I just make a really big document and then inkscape will crop that using the 'export-area-drawing flag. Works.
		await fileUtil.writeFile(path.join(r.scribusDirPath, "conv.py"), `from scribus import *
import scribus

scribus.newDocument((50000, 50000), (0, 0, 0, 0), scribus.PORTRAIT, 1, scribus.UNIT_POINTS, scribus.PAGE_1, 0, 1)
scribus.setUnit(scribus.UNIT_POINTS)
scribus.placeVectorFile("${r.f.input.rel}", 0, 0)
scribus.savePageAsEPS("${path.join(r.f.outDir.rel, "out.eps")}")
scribus.closeDoc()
scribus.fileQuit()`);
	}

	args = r => ["--prefs", r.scribusDirPath, "-ns", "-py", path.join(path.basename(r.scribusDirPath), "conv.py"), r.f.input.rel]
	runOptions = ({timeout : xu.MINUTE, virtualX : true})
	chain = "inkscape"
}


/*
const SCRIBUS_PREFS_DIR_PATH = "/mnt/ram/dexvert/scribus";

export class scribus extends Server
{
	async start()
	{


"use strict";
const XU = require("@sembiance/xu"),
	fs = require("fs"),
	fileUtil = require("@sembiance/xutil").file,
	tiptoe = require("tiptoe"),
	path = require("path");

const SCRIBUS_PREFS_DIR_PATH = "/mnt/ram/dexvert/scribus";
const SCRIBUS_PREF_FILENAMES = [".neversplash", "checkfonts150.xml", "prefs150.xml", "scribus150.rc", "scribusshapes.xml"];

exports.meta =
{
	website        : "https://www.scribus.net/",
	gentooPackage  : "app-office/scribus",
	gentooUseFlags : "boost minimal pdf templates",
	unsafe         : true
};

exports.bin = () => "scribus";
exports.args = (state, p, r, inPath="conv.py") => (["--prefs", SCRIBUS_PREFS_DIR_PATH, "-ns", "-py", inPath]);


exports.pre = (state, p, r, cb) =>
{
	tiptoe(
		function createPrefsDir()
		{
			fs.mkdir(SCRIBUS_PREFS_DIR_PATH, {recursive : true}, this);
		},
		function checkPrefsExistance()
		{
			SCRIBUS_PREF_FILENAMES.parallelForEach((SCRIBUS_PREF_FILENAME, subcb) => fileUtil.exists(path.join(SCRIBUS_PREFS_DIR_PATH, SCRIBUS_PREF_FILENAME), subcb), this);
		},
		function copyMissingPrefs(missingScribusPrefFiles)
		{
			missingScribusPrefFiles.parallelForEach((prefFileExists, subcb, i) =>
			{
				if(!prefFileExists)
					fs.copyFile(path.join(__dirname, "..", "..", "..", "scribus", SCRIBUS_PREF_FILENAMES[i]), path.join(SCRIBUS_PREFS_DIR_PATH, SCRIBUS_PREF_FILENAMES[i]), subcb);
				else
					setImmediate(subcb);
			}, this);
		},
		function createConversionScript()
		{
			
		},
		cb
	);
};

exports.post = (state, p, r, cb) => p.util.program.run("inkscape", {argsd : ["outfile.eps"]})(state, p, cb);

exports.runOptions = () => ({timeout : XU.MINUTE, virtualX : true, killSignal : "SIGTERM"});	// scribus won't kill with SIGINT
*/
