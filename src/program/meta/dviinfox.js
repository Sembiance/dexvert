/*
import {Program} from "../../Program.js";

export class dviinfox extends Program
{
	website = "http://tug.org/texlive/";
	gentooPackage = "app-text/texlive";
	gentooUseFlags = "X cjk extra graphics metapost png texi2html truetype xetex xml";
	informational = true;
}
*/

/*
"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	website        : "http://tug.org/texlive/",
	gentooPackage  : "app-text/texlive",
	gentooUseFlags : "X cjk extra graphics metapost png texi2html truetype xetex xml",
	informational  : true
};

exports.bin = () => "dviinfox";
exports.args = (state, p, r, inPath=state.input.filePath) => ([inPath]);
exports.post = (state, p, r, cb) =>
{
	const meta = {};
	(r.results || "").trim().split("\n").forEach(line =>
	{
		const {key, val} = (line.trim().match(/^\s*(?<key>[^:]+):\s*"?(?<val>[^"]+)"?$/) || {groups : {}}).groups;
		if(!key || !val || key.trim().length===0 || val.trim().length===0)
			return;

		meta[key.trim().toCamelCase()] = val.trim();
	});

	Object.assign(r.meta, meta);

	setImmediate(cb);
};
*/
