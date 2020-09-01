"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website       : ["http://he.fi/bchunk/", "https://www.mars.org/home/rob/proj/hfs/", "https://www.sudo.ws/", "https://www.gnu.org/software/libcdio/", "https://cdemu.sourceforge.io", "https://www.gnu.org/software/vcdimager/"],
	gentooPackage : ["app-cdr/bchunk", "sys-fs/hfsutils", "app-admin/sudo", "dev-libs/libcdio-paranoia", "app-cdr/cdemu", "media-video/vcdimager"],
	bin           : ["bchunk", "*", "sudo", "libcdio-paranoia", "*"]
};

exports.bin = () => path.join(__dirname, "..", "..", "..", "bin", "uniso");
exports.args = (state, p, inPath=state.input.filePath, outPath=state.output.dirPath) => ([`--tmpDirPath=${state.tmpDirPath}`, inPath, outPath]);
