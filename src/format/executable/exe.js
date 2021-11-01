"use strict";
const XU = require("@sembiance/xu"),
	C = require("../../C.js");

exports.meta =
{
	name     : "MS-DOS/Windows Executable",
	website  : "http://fileformats.archiveteam.org/wiki/EXE",
	ext      : [".exe"],
	magic    :
	[
		"Generic Win/DOS Executable", "DOS Executable Generic", /MS-DOS [Ee]xecutable/, /^Win\d\d Executable/, /compressed DOS Executable$/, "DOS Executable (alternate ZM id)", "16bit DOS EXE PKLite compressed",
		"PE32 executable", /^Win\d\d Executable/, "Win16 NE executable"
	],
	priority : C.PRIORITY.LOW
};

// We throw msdos/win executables at deark and 7z which can often extract various embedded cursors, icons and images
// We only do it if meta.exe is found, otheriwse we want a different format to handle this (such as dll)
exports.converterPriority = (state, p) =>
{
	if(!state.input.meta[p.format.meta.formatid])
		return [];
	
	return [{program : "7z", flags : {"7zType" : "PE", "7zRSRCOnly" : true}}, "deark"];
};

exports.inputMeta = (state0, p0, cb) => p0.util.flow.serial([
	() => ({program : "winedump"}),
	(state, p) =>
	{
		const winedumpMeta = p.util.program.getMeta(state, "winedump");
		// If we have meta from winedump and it's not a DLL file, then set the meta.exe which will allow deark to run later and processed = true to be set in executable.js
		if(winedumpMeta && !(winedumpMeta?.fileheader?.characteristics || []).includes("DLL"))
			state.input.meta[p.format.meta.formatid] = winedumpMeta;
		
		return p.util.flow.noop;
	}
])(state0, p0, cb);
