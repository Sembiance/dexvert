"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website       : ["http://he.fi/bchunk/", "https://www.mars.org/home/rob/proj/hfs/", "https://www.sudo.ws/", "https://www.gnu.org/software/libcdio/", "https://cdemu.sourceforge.io", "https://www.gnu.org/software/vcdimager/", "http://xmlstar.sourceforge.net/"],
	gentooPackage : ["app-cdr/bchunk", "sys-fs/hfsutils", "app-admin/sudo", "dev-libs/libcdio-paranoia", "app-cdr/cdemu", "media-video/vcdimager", "app-text/xmlstarlet"],
	bin           : ["bchunk", "*", "sudo", "libcdio-paranoia", "*"]
};

exports.bin = () => path.join(__dirname, "..", "..", "..", "bin", "uniso");
exports.args = (state, p, r, inPath=state.input.filePath, outPath=state.output.dirPath) => ([inPath, outPath]);
