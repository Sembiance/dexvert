"use strict";
const XU = require("@sembiance/xu"),
	path = require("path"),
	tiptoe = require("tiptoe"),
	fileUtil = require("@sembiance/xutil").file,
	C = require(path.join(__dirname, "..", "..", "C.js"));

exports.meta =
{
	name           : "Binary Text",
	website        : "http://fileformats.archiveteam.org/wiki/BIN_(Binary_Text)",
	ext            : [".bin"],
	mimeType       : "text/x-binary",
	forbiddenMagic : C.TEXT_MAGIC,
	bruteUnsafe    : true
};

exports.converterPriorty = ["abydosconvert", "ffmpeg", "ansilove"];

exports.inputMeta = (state, p, cb) =>
{
	tiptoe(
		function getArchiveComment()
		{
			p.util.program.run(p.program.ffprobe)(state, p, this);
		},
		function stashResults()
		{
			// Check to see if we have an archive comment
			let seenFormatSection = false;
			const meta = {};
			if(state.run.ffprobe && state.run.ffprobe.length>0 && state.run.ffprobe[0] && state.run.ffprobe[0].trim().length>0)
			{
				state.run.ffprobe[0].trim().split("\n").forEach(line =>
				{
					if(line.trim()==="format_long_name=Binary text")
						meta.formatLongName = line.trim();

					if(line.trim()==="[FORMAT]")
					{
						seenFormatSection = true;
						return;
					}

					if(!seenFormatSection)
						return;
					
					const tag = (line.trim().match(/^TAG:(?<key>[^=]+)=(?<value>.+)$/) || {groups : {}}).groups;
					if(tag.key && tag.value && tag.key.trim().length>0 && tag.value.trim().length>0)
						meta[tag.key.trim()] = tag.value.trim();
				});
			}
			if(Object.keys(meta).length>0)
				state.input.meta.binaryText = meta;

			this();
		},
		cb
	);
};

exports.updateProcessed = (state, p, cb) =>
{
	if(state.input.meta.binaryText && Object.keys(state.input.meta.binaryText).length>0)
		return setImmediate(cb);

	delete state.processed;

	const outputFilePaths = (state.output.files || []).slice();
	delete state.output.files;
	outputFilePaths.parallelForEach((outSubPath, subcb) => fileUtil.unlink(path.join(state.output.absolute, outSubPath), subcb), cb);
};
