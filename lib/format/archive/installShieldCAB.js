"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name          : "InstallShield CAB",
	website       : "http://fileformats.archiveteam.org/wiki/InstallShield_CAB",
	ext           : [".cab"],
	magic         : ["InstallShield CAB"],
	keepFilename  : true,
	filesOptional : (state, otherFiles) =>
	{
		const ourExt = state.input.ext.toLowerCase();
		// .cab files may also have a corresponding .hdr file
		if(ourExt===".cab")
			return otherFiles.filter(otherFile => otherFile.toLowerCase()===`${state.input.name.toLowerCase()}.hdr`);

		return false;
	}
};

exports.preSteps = [state => { state.processed = state.processed || state.input.ext.toLowerCase()===".hdr"; }];

exports.converterPriorty = ["unshield"];
