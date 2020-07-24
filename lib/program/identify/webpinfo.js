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
exports.args = state => ([state.input.filePath]);
