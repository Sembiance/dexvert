/*
import {Program} from "../../Program.js";

export class svgInfo extends Program
{
	website = "https://github.com/Sembiance/dexvert/bin/svgInfo.js";
	informational = true;
}
*/

/*
"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website       : "https://github.com/Sembiance/dexvert/bin/svgInfo.js",
	informational : true
};

exports.bin = () => path.join(__dirname, "..", "..", "..", "bin", "svgInfo.js");
exports.args = (state, p, r, inPath=state.input.filePath) => (["--jsonOutput", inPath]);
exports.post = (state, p, r, cb) =>
{
	let meta = {};
	if((r.results || "").trim().length>0)
	{
		try
		{
			const svgInfo = JSON.parse(r.results.trim());
			if(Object.keys(svgInfo.length>0))
				meta = svgInfo;
		}
		catch (err) {}
	}

	Object.assign(r.meta, meta);

	setImmediate(cb);
};
*/
