"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	website        : "https://www.gnu.org/software/libcdio",
	gentooPackage  : "dev-libs/libcdio",
	gentooUseFlags : "cddb cxx",
	informational  : true
};

exports.bin = () => "iso-info";
exports.args = state => ([state.input.filePath]);
