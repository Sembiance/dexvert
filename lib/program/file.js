"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

const MAGIC_FILE_PATH = path.join(__dirname, "..", "..", "share", "dexvert-magic.mgc");

exports.meta =
{
	website        : "https://www.darwinsys.com/file/",
	gentooPackage  : "sys-apps/file",
	gentooUseFlags : "bzip2 lzma seccomp zlib",
	informational  : true
};

exports.bin = () => "file";
exports.args = state => (["-m", MAGIC_FILE_PATH, "-b", state.input.filePath]);
