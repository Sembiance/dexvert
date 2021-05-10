"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	website        : "https://github.com/MediaArea/MediaInfo",
	gentooPackage  : "media-video/mediainfo",
	gentooUseFlags : "curl mms",
	informational  : true
};

exports.bin = () => "mediainfo";
exports.args = (state, p, r, inPath=state.input.filePath) => ([inPath]);
exports.post = (state, p, r, cb) =>
{
	const meta = {};
	(r.results || "").trim().split("\n").forEach(line =>
	{
		const {key, val} = (line.trim().match(/^(?<key>[^:]+):\s*(?<val>.+)$/) || {groups : {}}).groups;
		if(!key || !val || key.trim().length===0 || val.trim().length===0)
			return;

		meta[key.trim().toCamelCase()] = val.trim();
	});

	Object.assign(r.meta, meta);

	setImmediate(cb);
};
