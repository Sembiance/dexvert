"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	website        : "http://p7zip.sourceforge.net/",
	gentooPackage  : "app-arch/p7zip",
	gentooUseFlags : "pch",
	bruteUnsafe    : true
};

exports.bin = () => "7z";
exports.args = state => (["x", `-o${state.output.dirPath}`, state.input.filePath]);
