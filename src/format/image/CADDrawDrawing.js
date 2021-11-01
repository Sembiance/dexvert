/*
import {Format} from "../../Format.js";

export class CADDrawDrawing extends Format
{
	name = "TommySoftware CAD/Draw Drawing";
	website = "https://archive.org/details/t425l1e_zip";
	ext = [".t4g",".t3g",".t2g",".mpg"];
	forbidExtMatch = true;
	magic = ["TommySoftware CAD/Draw drawing","CAD/Draw TVG"];
	converters = undefined
}
*/
/*
"use strict";
const XU = require("@sembiance/xu"),
	fileUtil = require("@sembiance/xutil").file;

exports.meta =
{
	name           : "TommySoftware CAD/Draw Drawing",
	website        : "https://archive.org/details/t425l1e_zip",
	ext            : [".t4g", ".t3g", ".t2g", ".mpg"],
	forbidExtMatch : true,
	magic          : ["TommySoftware CAD/Draw drawing", "CAD/Draw TVG"]
};

exports.converterPriority = s0 =>
{
	const converters = [];
	const ext = s0.input.ext.toLowerCase();

	if(ext===".mpg")
		converters.push("MPG_T2G");
	else if(ext===".t2g")
		converters.push("T2G_T3G");
	else if(ext===".t3g")
		converters.push("T3G_T4G");
	else
		converters.push("CADDraw");
	
	converters.push({program : "dexvert", flags : {deleteInput : true}, argsd : state =>
	{
		// Find the result file from the previous converter and use it as the input for dexvert
		const availableFiles = fileUtil.globSync(state.output.absolute, "**", {nodir : true});
		if(!availableFiles || availableFiles.length!==1)
			return ["/dev/null"];
		
		return [availableFiles[0]];
	}});

	return [converters];
};

*/
