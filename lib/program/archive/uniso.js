"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website       : ["http://he.fi/bchunk/", "https://www.mars.org/home/rob/proj/hfs/", "https://www.sudo.ws/"],
	gentooPackage : ["app-cdr/bchunk", "sys-fs/hfsutils", "app-admin/sudo"],
	bin           : ["bchunk", "*", "sudo"]
};

exports.bin = () => path.join(__dirname, "..", "..", "..", "bin", "uniso");
exports.args = state => ([`--tmpDirPath=${state.tmpDirPath}`, state.input.absolute, state.output.absolute]);
