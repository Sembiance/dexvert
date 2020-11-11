"use strict";
const XU = require("@sembiance/xu"),
	fs = require("fs"),
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
exports.supportedInputMeta = function supportedInputMeta(state, p, cb)
{
	tiptoe(
		function getInfo()
		{
			fs.readFile(state.input.absolute, XU.UTF8, this.parallel());
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
