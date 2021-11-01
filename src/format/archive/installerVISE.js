"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name        : "Installer VISE Package",
	website     : "https://en.wikipedia.org/wiki/Installer_VISE",
	ext         : [".mac"],
	magic       : ["Installer VISE Mac package"],
	unsupported : true,
	notes       : "Haven't found non-mac files yet. They appear to be self extracting, so I could just run them under a MAC emulator to get the files out."
};
