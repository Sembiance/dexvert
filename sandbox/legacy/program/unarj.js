"use strict";
const XU = require("@sembiance/xu");

// This fails on a whole bunch of ARJ archives. 'unar' does a much better job

exports.meta =
{
	website        : "http://www.arjsoftware.com/",
	gentooPackage  : "app-arch/unarj"
};

exports.bin = () => "unarj";
exports.cwd = state => state.output.absolute;
exports.args = state => (["x", state.input.filePath]);
