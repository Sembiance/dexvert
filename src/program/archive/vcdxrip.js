"use strict";
const XU = require("@sembiance/xu"),
	tiptoe = require("tiptoe"),
	fs = require("fs"),
	runUtil = require("@sembiance/xutil").run,
	path = require("path");

exports.meta =
{
	website        : ["https://www.gnu.org/software/vcdimager", "http://xmlstar.sourceforge.net/"],
	gentooPackage  : ["media-video/vcdimager", "app-text/xmlstarlet"],
	bin            : ["vcdxrip", "xmlstarlet"],
	gentooUseFlags : "xml",
	unsafe    : true
};

exports.bin = () => "vcdxrip";

exports.args = (state, p, r, inPath=state.input.filePath) => ([`--nofiles`, `--bin-file=${path.relative(state.output.absolute, path.join(state.cwd, inPath))}`]);
exports.runOptions = state => ({cwd : state.output.absolute});

exports.post = (state, p, r, cb) =>
{
	tiptoe(
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
