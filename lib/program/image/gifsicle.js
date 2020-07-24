"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	website       : "https://www.lcdf.org/~eddietwo/gifsicle/",
	gentooPackage : "media-gfx/gifsicle",
	informational : true
};

exports.bin = () => "gifsicle";
exports.args = state => (["-I", state.input.filePath]);
exports.runOptions = () => ({"ignore-stderr" : true});
