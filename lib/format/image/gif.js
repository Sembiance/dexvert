"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name      : "Graphics Interchange Format",
	website   : "http://fileformats.archiveteam.org/wiki/GIF",
	ext       : [".gif"],
	mimeType  : "image/gif",
	magic     : ["GIF image data", /^GIF8[79]a bitmap$/],
	untouched : true
};

exports.inputMeta = (state0, p0, cb) => p0.util.flow.serial([
	(state, p) => p.family.supportedInputMeta,
	(state, p) =>
	{
		// Some GIF files are corrupted. If so, use nconvert to convert them to PNG
		if((state?.input?.meta?.image?.height||0)>0)
			return p.util.flow.noop;
		
		if(state?.id?.untouched)
			delete state.id.untouched;

		return ({program : "nconvert"});
	},
	() => ({program : "gifsicle"}),
	(state, p) =>
	{
		if(p.util.program.getMeta(state, "gifsicle"))
			state.input.meta.gif = p.util.program.getMeta(state, "gifsicle");

		return p.util.flow.noop;
	}
])(state0, p0, cb);
