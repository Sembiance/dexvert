"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name          : "InstallShield CAB",
	website       : "http://fileformats.archiveteam.org/wiki/InstallShield_CAB",
	ext           : [".cab"],
	magic         : ["InstallShield CAB", "InstallShield Cabinet archive", "InstallShield compressed Archive"],
	keepFilename  : true,
	filesOptional : (state, otherFiles) =>
	{
		const ourExt = state.input.ext.toLowerCase();
		
		// .cab files often require .hdr files to extract, even a data2.cab would need a data1.hdr, so let's grab all .hdr files
		if(ourExt===".cab")
			return otherFiles.filter(otherFile => otherFile.toLowerCase().endsWith(".hdr"));

		return false;
	}
};

exports.preSteps = [state => { state.processed = state.processed || state.input.ext.toLowerCase()===".hdr"; }];

exports.converterPriority =
[
	"unshield",
	{program : "unshield", flags : {unshieldUseOldCompression : true}},
	"winPack",
	"gameextractor",
	"UniExtract"
];
