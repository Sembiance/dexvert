/*
import {Program} from "../../Program.js";

export class unzip extends Program
{
	website = "http://infozip.sourceforge.net/";
	package = "app-arch/unzip";
	notes = "\nThe version in dexvert overlay includes several patches such as:\n* Support for USE_SMITH via an unreduce_full.c patch from ftp://ftp.info-zip.org/pub/infozip/src/unreduce_full.zip\n* Custom patch to prevent archive comments (sample svga.exe) from forcing user input to continue extraction";
}
*/

/*
"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	website        : "http://infozip.sourceforge.net/",
	package  : "app-arch/unzip",
	notes          : XU.trim`
		The version in dexvert overlay includes several patches such as:
		* Support for USE_SMITH via an unreduce_full.c patch from ftp://ftp.info-zip.org/pub/infozip/src/unreduce_full.zip
		* Custom patch to prevent archive comments (sample svga.exe) from forcing user input to continue extraction`
};

exports.bin = () => "unzip";

// By passing 'nopasswd' to -P it avoids the program hanging when an archive requires a password
exports.args = (state, p, r, inPath=state.input.filePath, outPath=state.output.dirPath) => (["-od", outPath, "-P", "nopasswd", inPath]);
*/
