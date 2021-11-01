/*
import {Format} from "../../Format.js";

export class lzx extends Format
{
	name = "Lempel-Ziv Archive";
	website = "http://fileformats.archiveteam.org/wiki/LZX";
	ext = [".lzx"];
	magic = ["LZX compressed archive","LZX Amiga compressed archive"];
	converters = ["unar","UniExtract"]

postSteps = [null,null];
}
*/
/*
"use strict";
const XU = require("@sembiance/xu"),
	fileUtil = require("@sembiance/xutil").file,
	path = require("path"),
	fs = require("fs");

exports.meta =
{
	name    : "Lempel-Ziv Archive",
	website : "http://fileformats.archiveteam.org/wiki/LZX",
	ext     : [".lzx"],
	magic   : ["LZX compressed archive", "LZX Amiga compressed archive"]
};

exports.converterPriority = ["unar", "UniExtract"];

// Sadly unar doesn't apply proper dates, so we use the 'unlzx' in list only mode to get our dates and then apply after extraction manually
exports.postSteps =
[
	() => ({program : "unlzx", flags : {unlzxListOnly : true}}),
	() => (state, p, cb) =>
	{
		const unlzxMeta = p.util.program.getMeta(state, "unlzx");
		if(!unlzxMeta || !unlzxMeta.fileProps)
			return setImmediate(cb);
		
		Object.entries(unlzxMeta.fileProps).parallelForEach(([filename, props], subcb) =>
		{
			const outFilePath = path.join(state.output.absolute, filename);
			if(!fileUtil.existsSync(outFilePath))
				return setImmediate(subcb);

			fs.utimes(outFilePath, props.ts, props.ts, subcb);
		}, cb);
	}
];

*/
