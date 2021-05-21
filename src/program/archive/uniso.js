"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website       : ["https://www.mars.org/home/rob/proj/hfs/", "https://www.sudo.ws/", "https://www.kernel.org/pub/linux/utils/util-linux/"],
	gentooPackage : ["sys-fs/hfsutils", "app-admin/sudo", "sys-apps/util-linux"],
	bin           : ["*", "sudo", "mount"]
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
