"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	website       : "https://www.rarlab.com/rar_add.htm",
	gentooPackage : "app-arch/unrar"
};

exports.bin = () => "unrar";
exports.args = state => (["x", "-p-", state.input.filePath, state.output.dirPath]);
