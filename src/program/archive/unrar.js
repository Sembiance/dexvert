/*
import {Program} from "../../Program.js";

export class unrar extends Program
{
	website = "https://www.rarlab.com/rar_add.htm";
	package = "app-arch/unrar";
}
*/

/*
"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	website       : "https://www.rarlab.com/rar_add.htm",
	package : "app-arch/unrar"
};

exports.bin = () => "unrar";
exports.args = (state, p, r, inPath=state.input.filePath, outPath=state.output.dirPath) => (["x", "-p-", inPath, outPath]);
exports.post = (state, p, r, cb) =>
{
	const meta = {};

	if((r.results || "").length>0)
	{
		const commentGroups = (r.results.replaceAll("\n", "§").match(/Extracting from in\.rar§(?<comment>.+)§§Extracting/) || {groups : {}}).groups;
		if(commentGroups.comment)
			meta.comment = commentGroups.comment.replaceAll("§", "\n").trim();
	}

	Object.assign(r.meta, meta);

	setImmediate(cb);
};
*/
