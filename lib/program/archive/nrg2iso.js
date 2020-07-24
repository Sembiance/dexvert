"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	website       : "http://gregory.kokanosky.free.fr/v4/linux/nrg2iso.en.html",
	gentooPackage : "app-cdr/nrg2iso"
};

exports.bin = () => "nrg2iso";
exports.args = state => ([state.input.filePath, `${state.input.filePath}.iso`]);
