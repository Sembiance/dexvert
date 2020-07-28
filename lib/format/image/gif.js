"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Graphics Interchange Format",
	website  : "http://fileformats.archiveteam.org/wiki/GIF",
	ext      : [".gif"],
	mimeType : "image/gif",
	magic    : ["GIF image data", /^GIF8[79]a bitmap$/]
};

exports.inputMeta = (state0, p0, cb) => p0.util.flow.serial([
	(state, p) => p.family.supportedInputMeta,
	() => ({program : "gifsicle"}),
	(state, p) =>
	{
		if(state.run.gifsicle[0].split("\n").some(line => line.trim().match(/^\* .+ \d+ images$/)))
			state.input.meta.gif = {animated : true};

		return p.util.flow.noop;
	}
])(state0, p0, cb);
