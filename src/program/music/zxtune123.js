"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website       : "https://zxtune.bitbucket.io/",
	gentooPackage : "media-sound/zxtune",
	gentooOverlay : "dexvert"
};

exports.bin = () => "zxtune123";
exports.args = (state, p, r, inPath=state.input.filePath, outPath=path.join(state.output.dirPath, "outfile.wav")) => (["--file", inPath, `--wav=filename=${outPath}`]);
exports.post = (state, p, r, cb) =>
{
	const meta = {};

	(r.results || "").trim().replaceAll("\t", "\n").split("\n").forEach(line =>
	{
		const {key, val} = (line.trim().match(/^(?<key>[^:]+)\s*:\s*(?<val>.+)$/) || {groups : {}}).groups;
		if(key && ["type", "container", "title", "author", "program"].includes(key.trim().toLowerCase()) && val && val.trim().length>0)
			meta[key.trim().toLowerCase()] = val.trim();
	});

	Object.assign(r.meta, meta);

	if(Object.keys(meta).length>0)
		state.input.meta.music = meta;

	return p.util.file.move(path.join(state.output.absolute, "outfile.wav"), path.join(state.output.absolute, `${state.input.name}.wav`))(state, p, cb);
};
