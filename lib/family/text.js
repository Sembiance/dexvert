"use strict";
const XU = require("@sembiance/xu"),
	fs = require("fs"),
	runUtil = require("@sembiance/xutil").run,
	tiptoe = require("tiptoe");

exports.steps =
[
	(state, p) => (p.format.steps ? p.util.flow.serial(p.format.steps) : p.util.flow.noop),
	(state, p) => p.format.post || p.util.flow.noop
];

exports.updateProcessed = function updateProcessed(state, p, cb)
{
	// Archive extraction is successful if there are any files. Don't return because format might override this and set processed back to false
	if(state.output.files)
		state.processed = true;

	if(p.format.updateProcessed)
		return p.format.updateProcessed(state, p, cb);
	
	setImmediate(cb);
};

// Standard inputMeta function for music files we support
exports.supportedInputMeta = function supportedInputMeta(state, p, cb)
{
	tiptoe(
		function getInfo()
		{
			fs.readFile(state.input.absolute, XU.UTF8, this.parallel());
			runUtil.run("chardetect", [state.input.filePath], {silent : true, cwd : state.cwd}, this.parallel());
		},
		function saveMeta(textRaw, detectedEncodingRaw)
		{
			const lineCount = textRaw.split(textRaw.includes("\n") ? "\n" : "\r").length;
			if(lineCount>0)
			{
				const textMeta = {lineCount, encoding : {}};
				if(state.id.encoding)
					textMeta.encoding.declared = state.id.encoding;
				
				let detectedEncoding = detectedEncodingRaw.substring(state.input.filePath.length + 2);
				if(detectedEncoding!=="no result")
				{
					detectedEncoding = detectedEncoding.substring(0, detectedEncoding.indexOf(" "));
					if(detectedEncoding.length>0)
						textMeta.encoding.detected = detectedEncoding;
				}

				if(Object.keys(textMeta.encoding).length===0)
					delete textMeta.encoding;

				state.input.meta.text = textMeta;
				state.processed = true;
			}
			
			this();
		},
		cb
	);
};
