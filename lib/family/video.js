"use strict";
const XU = require("@sembiance/xu"),
	videoUtil = require("@sembiance/xutil").video,
	tiptoe = require("tiptoe");

exports.steps =
[
	(state, p) => p.util.flow.serial(p.format.steps),
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

// Standard inputMeta function for videos we support
exports.supportedInputMeta = function supportedInputMeta(state, p, cb)
{
	tiptoe(
		function getImageInfo()
		{
			videoUtil.getInfo(state.input.absolute, this);
		},
		function stashResults(videoInfo)
		{
			if(videoInfo && videoInfo.width && videoInfo.height)
			{
				state.input.meta.video = videoInfo;
				if(p.format.meta.browserNative)
					state.processed = true;
			}

			this();
		},
		cb
	);
};
