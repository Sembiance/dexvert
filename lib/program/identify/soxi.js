"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	website        : "http://sox.sourceforge.net",
	gentooPackage  : "media-sound/sox",
	gentooUseFlags : "alsa amr encode flac id3tag mad ogg openmp png sndfile twolame wavpack",
	informational  : true
};

exports.bin = () => "soxi";
exports.args = (state, p, inPath=state.input.filePath) => ([inPath]);
exports.post = (state, p, cb) =>
{
	const meta = {};
	((state.run.soxi || [])[0] || "").trim().split("\n").forEach(line =>
	{
		const {key, val} = (line.trim().match(/^(?<key>[^:]+)\s*:\s*(?<val>.+)$/) || {groups : {}}).groups;
		if(key && val && !["Input File", "Comments", "File Size"].some(v => key.trim().startsWith(v)))
		{
			const properKey = key.trim().toCamelCase();
			meta[properKey] = (["channels", "sampleRate"].some(v => properKey===v) ? +val.trim() : val.trim());
		}
	});

	if(Object.keys(meta).length>0)
		state.run.meta.soxi = meta;

	setImmediate(cb);
};
