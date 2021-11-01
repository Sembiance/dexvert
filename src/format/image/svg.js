/*
import {Format} from "../../Format.js";

export class svg extends Format
{
	name = "Scalable Vector Graphics";
	website = "http://fileformats.archiveteam.org/wiki/Scalable_Vector_Graphics";
	ext = [".svg",".svgz"];
	mimeType = "image/svg+xml";
	magic = ["SVG Scalable Vector Graphics image"];
	untouched = true;

inputMeta = undefined;
}
*/
/*
"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name      : "Scalable Vector Graphics",
	website   : "http://fileformats.archiveteam.org/wiki/Scalable_Vector_Graphics",
	ext       : [".svg", ".svgz"],
	mimeType  : "image/svg+xml",
	magic     : ["SVG Scalable Vector Graphics image"],
	untouched : true
};

exports.inputMeta = (state0, p0, cb) => p0.util.flow.serial([
	() => ({program : "svgInfo"}),
	(state, p) =>
	{
		const svgInfo = p.util.program.getMeta(state, "svgInfo");
		if(svgInfo)
		{
			state.input.meta.image = svgInfo;
			if(svgInfo.width && svgInfo.height)
				state.processed = true;
		}
		
		return p.util.flow.noop;
	}
])(state0, p0, cb);

*/
