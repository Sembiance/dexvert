"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	website        : "http://lallafa.de/blog/amiga-projects/amitools/",
	gentooPackage  : "app-arch/amitools",
	gentooOverlay  : "dexvert"
};

exports.bin = () => "xdftool";
exports.args = state => ([state.input.filePath, "unpack", state.output.dirPath]);
