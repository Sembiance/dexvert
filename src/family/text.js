"use strict";
const XU = require("@sembiance/xu"),
	C = require("../C.js"),
	fs = require("fs"),
	dexUtil = require("../dexUtil.js"),
	tiptoe = require("tiptoe");

exports.steps =
[
	(state, p) => (p.format.steps ? p.util.flow.serial(p.format.steps) : p.util.flow.noop),
	(state, p) => p.format.post || p.util.flow.noop
];

exports.updateProcessed = function updateProcessed(state, p, cb)
{
	if(state.output.files)
		state.processed = true;

	if(p.format.updateProcessed)
		return p.format.updateProcessed(state, p, cb);
	
	setImmediate(cb);
};

// Standard inputMeta function for text files we support
exports.supportedInputMeta = function supportedInputMeta(state, p, cb, inputFilePath=state.input.absolute)
{
	tiptoe(
		function getInfo()
		{
			fs.readFile(inputFilePath, XU.UTF8, this.parallel());
			p.util.program.run("file", {argsd : [state.input.filePath], flags : {allMatches : true}})(state, p, this.parallel());
			p.util.program.run("chardetect", {argsd : [state.input.filePath]})(state, p, this.parallel());
		},
		function saveMeta(textRaw)
		{
			const lineCount = textRaw.split(textRaw.includes("\n") ? "\n" : "\r").length;
			if(lineCount>0)
			{
				const textMeta = {lineCount, encoding : {}};
				if(state.id.encoding)
					textMeta.encoding.declared = state.id.encoding;
				
				const charDetectMeta = (p.util.program.getMeta(state, "chardetect") || {});
				if(charDetectMeta.encoding)
					textMeta.encoding.detected = charDetectMeta.encoding;

				if(Object.keys(textMeta.encoding).length===0)
					delete textMeta.encoding;

				const fileRunResult = (p.util.program.getRan(state, "file") || {});
				if(fileRunResult?.results && fileRunResult.results.trim().split("\n- ").some(v => C.TEXT_MAGIC.some(m => dexUtil.flexMatch(v.trimChars(",").trim(), m))))
					textMeta.verifiedAsText = true;

				state.input.meta.text = textMeta;

				// Only set processed to true if we were able to detect a text encoding or we have a 100% confidence this is a text match
				if(charDetectMeta.encoding || state.id.confidence===100)
					state.processed = true;
			}
			
			this();
		},
		cb
	);
};
