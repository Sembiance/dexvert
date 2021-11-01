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
exports.args = (state, p, r, inPath=state.input.filePath) => ([inPath]);
exports.post = (state, p, r, cb) =>
{
	const meta = {};

	(r.results || "").trim().split("\n").forEach(line =>
	{
		const {key, val} = (line.trim().match(/^(?<key>[^:]+)\s*:\s*(?<val>.+)$/) || {groups : {}}).groups;
		if(key && key==="ISO 9660 image")
			meta.isISO = true;
		if(key && val && !["ISO 9660 image", "iso-info", "++ WARN"].some(v => key.trim().startsWith(v)))
			meta[key.trim().toCamelCase()] = val.trim();
	});

	Object.assign(r.meta, meta);

	setImmediate(cb);
};
