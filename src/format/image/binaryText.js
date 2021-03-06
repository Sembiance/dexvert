"use strict";
const XU = require("@sembiance/xu"),
	tiptoe = require("tiptoe"),
	C = require("../../C.js");

exports.meta =
{
	name           : "Binary Text",
	website        : "http://fileformats.archiveteam.org/wiki/BIN_(Binary_Text)",
	ext            : [".bin"],
	mimeType       : "text/x-binary",
	forbiddenMagic : C.TEXT_MAGIC,
	unsafe         : true,
	notes          : "It's crazy hard to identify this file, and we err on the side of caution. So we only convert files that have meta data set in them."
};

// binaryText is often mistaken for other things. So don't allow if we had to transform the file to get here
exports.idCheck = state => !state.transformed;

// Also only proceed if the meta gathering was successful
// deark handles this format better than ansilove
exports.converterPriorty = state => ((state.input.meta.ansiArt || state.input.meta.binaryText) ? [{program : "deark", flags : {dearkCharOutput : "image"}}, {program : "ansilove", flags : {ansiloveType : "bin"}}, "abydosconvert", "ffmpeg"] : []);

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
