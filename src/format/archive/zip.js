/*
import {Format} from "../../Format.js";

export class zip extends Format
{
	name = "PKZip Archive";
	website = "http://fileformats.archiveteam.org/wiki/ZIP";
	ext = [".zip",".exe"];
	magic = ["ZIP compressed archive","Zip archive data","ZIP Format",{},{},"Zip multi-volume archive data"];
	converters = ["unzip","deark",{"program":"deark","flags":{"dearkOpts":["zip:scanmode"]}},"unar","7z","UniExtract"]

metaProviders = [""];

post = undefined;

updateProcessed = undefined;
}
*/
/*
"use strict";
const XU = require("@sembiance/xu");
const tiptoe = require("tiptoe");

exports.meta =
{
	name    : "PKZip Archive",
	website : "http://fileformats.archiveteam.org/wiki/ZIP",
	ext     : [".zip", ".exe"],
	magic   : ["ZIP compressed archive", "Zip archive data", "ZIP Format", /^PKZIP (mini-)?self-extracting 16bit DOS executable$/, /ZIP self-extracting archive/, "Zip multi-volume archive data"]		// eslint-disable-line prefer-named-capture-group
};

exports.converterPriority = ["unzip", "deark", {program : "deark", flags : {dearkOpts : ["zip:scanmode"]}}, "unar", "7z", "UniExtract"];

exports.inputMeta = (state, p, cb) =>
{
	tiptoe(
		function getArchiveComment()
		{
			p.util.program.run("unzip", {args : ["-qz", state.input.filePath]})(state, p, this);
		},
		function stashResults(r)
		{
			// Check to see if we have an archive comment
			if((r.results || "").trim().length>0 && !r.results.includes("End-of-central-directory signature not found"))
				state.input.meta.zip = {comment : r.results};	// Don't trim, to preserve whitespace

			this();
		},
		cb
	);
};

exports.post = (state, p, cb) =>
{
	const r = p.util.program.getRan(state, "unzip");

	// Check to see if we failed to extract due to the archive being password protected
	if((r.results || "").includes("incorrect password"))
		state.input.meta.zip = {passwordProtected : true};
		
	setImmediate(cb);
};

exports.updateProcessed = (state, p, cb) =>
{
	// If it's password protected or is a zip file with no files, then mark it as done, even though we were not able to extract the files, we know it is a zip file
	if(state.input.meta.zip?.passwordProtected || state.identify.some(o => o.magic==="Zip archive data (empty)"))
		state.processed = true;
	
	setImmediate(cb);
};

*/
