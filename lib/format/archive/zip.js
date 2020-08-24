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

exports.steps = [() => ({program : "unzip"})];

exports.inputMeta = (state, p, cb) =>
{
	tiptoe(
		function getArchiveComment()
		{
			p.util.program.run("unzip", {args : ["-qz", state.input.filePath]})(state, p, this);
		},
		function stashResults()
		{
			// Check to see if we have an archive comment
			if(state.run.unzip && state.run.unzip.length>0 && state.run.unzip[0] && state.run.unzip[0].trim().length>0)
				state.input.meta.zip = {comment : state.run.unzip[0].trim()};

			this();
		},
		cb
	);
};

exports.post = (state, p, cb) =>
{
	// Check to see if we failed to extract due to the archive being password protected
	if(state.run.unzip && state.run.unzip.length>0 && state.run.unzip[0].includes("incorrect password"))
		state.input.meta.zip = {passwordProtected : true};
		
	setImmediate(cb);
};

exports.updateProcessed = (state, p, cb) =>
{
	// If it's password protected, then mark it as done, even though we were not able to extract the files, we know it is a zip file
	if(state.input.meta.zip && state.input.meta.zip.passwordProtected)
		state.processed = true;
	
	setImmediate(cb);
};
