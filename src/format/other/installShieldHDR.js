"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name        : "InstallShield HDR",
	website     : "http://fileformats.archiveteam.org/wiki/InstallShield_CAB",
	ext         : [".hdr"],
	magic       : ["InstallShield CAB"],
	weakMagic   : true,
	unsupported : true,
	// In order to be an InstallShield HDR file, it must also have a .cab file
	filesRequired : (state, otherFiles) => otherFiles.filter(otherFile => otherFile.toLowerCase()===`${state.input.name.toLowerCase()}.cab`),
	notes         : "HDR files are meta data for installShieldCAB files and are not processed directly."
};
