"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	website        : "https://www.gnu.org/software/tar/",
	gentooPackage  : "app-arch/tar",
	gentooUseFlags : "acl nls xattr"
};

exports.bin = () => "tar";
exports.args = state => (["-xf", state.input.filePath, "-C", state.output.dirPath]);
