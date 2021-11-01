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
exports.args = (state, p, r, inPath=state.input.filePath) => ([inPath]);
exports.post = (state, p, r, cb) =>
{
	const meta = {};
	if((r.results || "").includes("can't open input file"))
		return setImmediate(cb);
		
	(r.results || "").trim().split("\n").forEach(line =>
	{
		const {key, val} = (line.trim().match(/^(?<key>[^:]+)\s*:\s*(?<val>.+)$/) || {groups : {}}).groups;
		if(key && val && !["Input File", "Comments", "File Size"].some(v => key.trim().startsWith(v)))
		{
			const properKey = key.trim().toCamelCase();
			if(properKey==="duration")
			{
				const parts = val.trim().match(/^(?<hour>\d+):(?<minute>\d+):(?<second>\d+)\.(?<ms>\d*)/).groups;
				meta[properKey] = [...["hour", "minute", "second"].map(v => (XU[v.toUpperCase()]*(+parts[v]))), (+parts.ms)].sum();
			}
			else
			{
				meta[properKey] = (["channels", "sampleRate"].includes(properKey) ? +val.trim() : val.trim());
			}
		}
	});

	Object.assign(r.meta, meta);

	setImmediate(cb);
};
