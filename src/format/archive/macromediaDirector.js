"use strict";
const XU = require("@sembiance/xu"),
	path = require("path"),
	fs = require("fs");

exports.meta =
{
	name           : "Macromedia Director",
	website        : "http://fileformats.archiveteam.org/wiki/Shockwave_(Director)",
	ext            : [".dir", ".dxr", ".drx", ".cxt", ".cst", ".dcr"],
	forbidExtMatch : true,
	magic          : ["Macromedia Director project", "Adobe Director Protected Cast", "Macromedia Director Protected Movie", "Director - Shockwave movie", "Generic RIFX container"],
	weakMagic      : ["Generic RIFX container"],
	keepFilename   : "extras",
	filesOptional  : (state, otherFiles, otherDirs=[]) => otherDirs.filter(otherDir => otherDir.toLowerCase()==="xtras"),
	notes          : "While 'xtras' is included here, it is NOT copied over into Windows. See more details in program/archive/macromediaDirector.js"
};

exports.steps =
[
	// We always start out with passing it to dirOpener
	// For 'protected' formats like DXR/CXT it will unprotect it
	// Other files that are really old are updated to a version that the MX 2004 will actually open
	// It handles both
	// If it doesn't need to do anything, it ends up producing an identical output file, but file.findValidOutputFiles() ends up taking care of detecting the dup and removing it
	() => ({program : "dirOpener"}),
	(state, p) => p.util.file.findValidOutputFiles(),
	state =>
	{
		// If dirOpener didn't produce a usable file, then we just pass the original input onto macromediaDirector
		if(!state.output.files?.length)
			return {program : "macromediaDirector"};
		
		// Otherwise we move the produced output from dirOpener to state.cwd and use that as the input for macromediaDirector
		const outputFilePath = path.join(state.output.absolute, state.output.files[0]);
		
		// We rename the file dexvert to ensure we don't collide with an existing filename, seems to fix some problems with 'find by.Dir' sample
		const cwdFilePath = path.join(state.cwd, `dexvert${path.extname(state.output.files[0]).toLowerCase()}`);
		fs.renameSync(outputFilePath, cwdFilePath);
		return {program : "macromediaDirector", argsd : [cwdFilePath]};
	},
	(state, p) => p.util.file.findValidOutputFiles(),
	() => exports.validateOutputFiles
];
