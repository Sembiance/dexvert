"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	website        : "https://developers.google.com/speed/webp/download",
	gentooPackage  : "media-libs/libwebp",
	gentooUseFlags : "gif jpeg opengl png tiff",
	informational  : true
};

exports.bin = () => "webpinfo";
exports.args = (state, p, inPath=state.input.filePath) => ([inPath]);
exports.post = (state, p, cb) =>
{
	const meta = {};

	if(state.run.webpinfo && state.run.webpinfo.length>0 && state.run.webpinfo[0] && state.run.webpinfo[0].trim().includes("Animation: 1"))
		meta.animated = true;

	if(Object.keys(meta).length>0)
		state.run.meta.webpinfo = meta;

	setImmediate(cb);
};
