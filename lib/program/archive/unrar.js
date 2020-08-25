"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	website       : "https://www.rarlab.com/rar_add.htm",
	gentooPackage : "app-arch/unrar"
};

exports.bin = () => "unrar";
exports.args = (state, p, inPath=state.input.filePath, outPath=state.output.dirPath) => (["x", "-p-", inPath, outPath]);
exports.post = (state, p, cb) =>
{
	const meta = {};

	if(state.run.unrar && state.run.unrar.length>0)
	{
		const commentGroups = (state.run.unrar[0].replaceAll("\n", "§").match(/Extracting from in\.rar§(?<comment>.+)§§Extracting/) || {groups : {}}).groups;
		if(commentGroups.comment)
			meta.comment = commentGroups.comment.replaceAll("§", "\n").trim();
	}

	if(Object.keys(meta).length>0)
		state.run.meta.unrar = meta;

	setImmediate(cb);
};
