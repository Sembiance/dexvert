"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	website        : "https://www.gnu.org/software/libcdio",
	gentooPackage  : "dev-libs/libcdio",
	gentooUseFlags : "cddb cxx",
	informational  : true
};

exports.bin = () => "iso-info";
exports.args = (state, p, inPath=state.input.filePath) => ([inPath]);
exports.post = (state, p, cb) =>
{
	const meta = {};

	((state.run["iso-info"] || [])[0] || "").trim().split("\n").forEach(line =>
	{
		const {key, val} = (line.trim().match(/^(?<key>[^:]+)\s*:\s*(?<val>.+)$/) || {groups : {}}).groups;
		if(key && val && !["ISO 9660 image", "iso-info", "++ WARN"].some(v => key.trim().startsWith(v)))
			meta[key.trim().toCamelCase()] = val.trim();
	});

	if(Object.keys(meta).length>0)
		state.run.meta["iso-info"] = meta;

	setImmediate(cb);
};
