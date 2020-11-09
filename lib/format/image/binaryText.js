"use strict";
const XU = require("@sembiance/xu"),
	path = require("path"),
	tiptoe = require("tiptoe"),
	fileUtil = require("@sembiance/xutil").file,
	C = require("../../C.js");

exports.meta =
{
	name           : "Binary Text",
	website        : "http://fileformats.archiveteam.org/wiki/BIN_(Binary_Text)",
	ext            : [".bin"],
	mimeType       : "text/x-binary",
	forbiddenMagic : C.TEXT_MAGIC,
	bruteUnsafe    : true,
	notes          : "It's crazy hard to identify this file, and we err on the side of caution. So we only convert files that have meta data set in them."
};

// deark handles things a lot better than ansilove
exports.converterPriorty = ["deark", {program : "ansilove", flags : {ansiloveType : "bin"}}, "abydosconvert", "ffmpeg"];

exports.inputMeta = (state, p, cb) =>
{
	tiptoe(
		function getArchiveComment()
		{
			p.util.program.run("ffprobe")(state, p, this.parallel());
			p.family.ansiArtInputMeta(state, p, this.parallel());
		},
		function stashResults()
		{
			if(p.util.program.getMeta(state, "ffprobe"))
				state.input.meta.binaryText = p.util.program.getMeta(state, "ffprobe");

			this();
		},
		cb
	);
};

// binaryText is often mistaken for other things, so only proceed if the meta gathering was successful
exports.updateProcessed = (state, p, cb) =>
{
	if((state.input.meta.ansiArt && Object.keys(state.input.meta.ansiArt).length>0) || (state.input.meta.binaryText && Object.keys(state.input.meta.binaryText).length>0))
		return setImmediate(cb);

	delete state.processed;

	const outputFilePaths = (state.output.files || []).slice();
	delete state.output.files;
	outputFilePaths.parallelForEach((outSubPath, subcb) => fileUtil.unlink(path.join(state.output.absolute, outSubPath), subcb), cb);
};
