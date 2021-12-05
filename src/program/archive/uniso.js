/*
import {Program} from "../../Program.js";

export class uniso extends Program
{
	website = ["https://www.mars.org/home/rob/proj/hfs/","https://www.sudo.ws/","https://www.kernel.org/pub/linux/utils/util-linux/"];
	package = ["sys-fs/hfsutils","app-admin/sudo","sys-apps/util-linux"];
	bin = ["*","sudo","mount"];
	flags = {"offset":"Extract ISO starting at this particular byte offset. Default: 0","hfs":"Set this to true to process the iso as a MacOS HFS disc. Default: false"};
}
*/

/*
"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website       : ["https://www.mars.org/home/rob/proj/hfs/", "https://www.sudo.ws/", "https://www.kernel.org/pub/linux/utils/util-linux/"],
	package : ["sys-fs/hfsutils", "app-admin/sudo", "sys-apps/util-linux"],
	bin           : ["*", "sudo", "mount"],
	flags         :
	{
		offset : "Extract ISO starting at this particular byte offset. Default: 0",
		hfs    : "Set this to true to process the iso as a MacOS HFS disc. Default: false"
	}
};

exports.bin = () => path.join(__dirname, "..", "..", "..", "bin", "uniso");
exports.args = (state, p, r, inPath=state.input.filePath, outPath=state.output.dirPath) =>
{
	const unisoArgs = [];
	if(r.flags.offset)
		unisoArgs.push(`--offset=${r.flags.offset}`);
	
	unisoArgs.push(inPath, outPath);
	if(r.flags.hfs)
		unisoArgs.push("hfs");

	return (unisoArgs);
};
*/
