/*
import {Program} from "../../Program.js";

export class vcdxrip extends Program
{
	website = ["https://www.gnu.org/software/vcdimager","http://xmlstar.sourceforge.net/"];
	package = ["media-video/vcdimager","app-text/xmlstarlet"];
	bin = ["vcdxrip","xmlstarlet"];
	unsafe = true;
}
*/

/*
"use strict";
const XU = require("@sembiance/xu"),
	tiptoe = require("tiptoe"),
	fs = require("fs"),
	runUtil = require("@sembiance/xutil").run,
	fileUtil = require("@sembiance/xutil").file,
	path = require("path");

exports.meta =
{
	website        : ["https://www.gnu.org/software/vcdimager", "http://xmlstar.sourceforge.net/"],
	package  : ["media-video/vcdimager", "app-text/xmlstarlet"],
	bin            : ["vcdxrip", "xmlstarlet"],
	unsafe    : true
};

exports.bin = () => "vcdxrip";

exports.args = (state, p, r, inPath=state.input.filePath) => ([`--nofiles`, `--bin-file=${path.relative(state.output.absolute, path.join(state.cwd, inPath))}`]);
exports.runOptions = state => ({cwd : state.output.absolute});

exports.post = (state, p, r, cb) =>
{
	tiptoe(
		function checkSuccess()
		{
			const avseqFilePath = path.join(state.output.absolute, "avseq01.mpg");
			if(!fileUtil.existsSync(avseqFilePath))
				return this();

			// If the output includes this message then the processing of the VCD failed somewhere and left an incomplete .mpg file
			// So we abort and delete the mpg file so that we can detect this failure later by lack of the mpg file and try somethign else (IsoBuster likely)
			if((r.results || "").includes("encountered non-form2 sector -- leaving loop"))
				return fileUtil.unlink(avseqFilePath, this), undefined;

			this();
		},
		function stripCommentsFromXML()
		{
			// vcdxrip creates an XML file with a comment with the current command being executed which causes this file to change from run to run due to temp dir, etc.
			// Supposed to be able to pass "--no-command-comment" to vcdxrip to prevent this, but it does not work for me. So we use xmlstarlet to strip out comments
			runUtil.run("xmlstarlet", ["-q", "c14n", "--without-comments", path.join(state.output.absolute, "videocd.xml")], {silent : true}, this);
		},
		function saveNewXMLFile(xmlRaw)
		{
			if(!xmlRaw || xmlRaw.length===0)
				return this();
			
			fs.writeFile(path.join(state.output.absolute, "videocd.xml"), `<?xml version="1.0"?>\n${xmlRaw}`, XU.UTF8, this);
		},
		cb
	);
};
*/
