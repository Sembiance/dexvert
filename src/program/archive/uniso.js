"use strict";
const XU = require("@sembiance/xu"),
	dexUtil = require("../../dexUtil.js"),
	path = require("path");

const HFS_MAGICS = [...require("../../format/archive/iso.js").HFS_MAGICS, ...require("../../format/archive/rawPartition.js").HFS_MAGICS];	// eslint-disable-line node/global-require

exports.meta =
{
	website       : ["https://www.mars.org/home/rob/proj/hfs/", "https://www.sudo.ws/", "https://www.kernel.org/pub/linux/utils/util-linux/"],
	gentooPackage : ["sys-fs/hfsutils", "app-admin/sudo", "sys-apps/util-linux"],
	bin           : ["*", "sudo", "mount"]
};

exports.bin = () => path.join(__dirname, "..", "..", "..", "bin", "uniso");
exports.args = (state, p, r, inPath=state.input.filePath, outPath=state.output.dirPath, isoType=(state.identify.some(identification => HFS_MAGICS.some(matchAgainst => dexUtil.flexMatch(identification.magic, matchAgainst))) ? "hfs" : "")) =>
{
	const unisoArgs = [];
	if(r.flags.offset)
		unisoArgs.push(`--offset=${r.flags.offset}`);

	return ([...unisoArgs, inPath, outPath, isoType]);
};
