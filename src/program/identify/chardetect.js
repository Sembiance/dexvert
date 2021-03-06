"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	website        : "https://github.com/chardet/chardet",
	gentooPackage  : "dev-python/chardet",
	informational  : true
};

exports.bin = () => "chardetect";
exports.args = (state, p, r, inPath=state.input.filePath) => ([inPath]);
exports.post = (state, p, r, cb) =>
{
	const meta = {};
	
	let detectedEncoding = (r.results || "").trim().substring(state.input.filePath.length + 2);
	if(detectedEncoding!=="no result")
	{
		detectedEncoding = detectedEncoding.substring(0, detectedEncoding.indexOf(" "));
		if(detectedEncoding.length>0)
			meta.encoding = detectedEncoding;
	}

	Object.assign(r.meta, meta);

	setImmediate(cb);
};
