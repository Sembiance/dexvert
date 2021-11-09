/*
import {Program} from "../../Program.js";

export class file extends Program
{
	website = "https://www.darwinsys.com/file/";
	gentooPackage = "sys-apps/file";
	gentooUseFlags = "bzip2 lzma seccomp zlib";
	informational = true;
	flags = {"allMatches":"Set this to true to return ALL matches from the file command, instead of just 1. Default: false"};
}
*/

/*
"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

const MAGIC_FILE_PATH = path.join(__dirname, "..", "..", "..", "file_magic", "dexvert-magic.mgc");

exports.meta =
{
	website        : "https://www.darwinsys.com/file/",
	gentooPackage  : "sys-apps/file",
	gentooUseFlags : "bzip2 lzma seccomp zlib",
	informational  : true,
	flags          :
	{
		allMatches : "Set this to true to return ALL matches from the file command, instead of just 1. Default: false"
	}
};

exports.bin = () => "file";
exports.args = (state, p, r, inPath=state.input.filePath) =>
{
	const fileArgs = ["--dereference", "--magic-file", MAGIC_FILE_PATH, "--brief"];
	if(r.flags.allMatches)
		fileArgs.push("--keep-going", "--raw");
	
	fileArgs.push(inPath);
	return fileArgs;
};
*/
