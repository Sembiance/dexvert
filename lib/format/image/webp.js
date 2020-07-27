"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name             : "WebP Image",
	website          : "http://fileformats.archiveteam.org/wiki/Webp",
	ext              : [".webp"],
	mimeType         : "image/webp",
	magic            : ["WebP bitmap", /^WebP$/, /^RIFF.* Web\/P image$/]
};

exports.inputMeta = (state0, p0, cb) => p0.util.flow.serial([
	(state, p) => p.family.supportedInputMeta,
	() => ({program : "webpinfo"}),
	(state, p) =>
	{
		if(state.run.webpinfo && state.run.webpinfo.length>0 && state.run.webpinfo[0] && state.run.webpinfo[0].trim().includes("Animation: 1"))
			state.input.meta.webp.animated = true;

		return p.util.flow.noop;
	}
])(state0, p0, cb);
