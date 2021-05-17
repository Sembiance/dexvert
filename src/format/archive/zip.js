"use strict";
const XU = require("@sembiance/xu");
const tiptoe = require("tiptoe");

exports.meta =
{
	name    : "PKZip Archive",
	website : "http://fileformats.archiveteam.org/wiki/ZIP",
	ext     : [".zip"],
	magic   : ["ZIP compressed archive", "Zip archive data", "ZIP Format", /^PKZIP (mini-)?self-extracting 16bit DOS executable$/]		// eslint-disable-line prefer-named-capture-group
};

exports.converterPriorty = ["unzip", "deark", {program : "deark", flags : {dearkOpts : ["zip:scanmode"]}}, "unar"];

exports.inputMeta = (state, p, cb) =>
{
	tiptoe(
		function getArchiveComment()
		{
			p.util.program.run("unzip", {args : ["-qz", state.input.filePath]})(state, p, this);
		},
		function stashResults()
		{
			const r = p.util.program.getRan(state, "unzip");
			// Check to see if we have an archive comment
			if((r.results || "").trim().length>0 && !r.results.includes("End-of-central-directory signature not found"))
				state.input.meta.zip = {comment : r.results.trim()};

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
