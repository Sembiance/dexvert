"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name  : "Microsoft Windows Dynmic Link Library",
	ext   : [".dll"],
	magic : ["Win32 Dynamic Link Library", "PE32 executable (DLL)", "MS-DOS executable, NE for MS Windows 3.x (DLL or font)"]
};

// We throw DLLs at deark which can often extract various embedded cursors, icons and images
exports.steps = [(state, p) => (state.input.meta[p.format.meta.formatid] ? ({program : "deark"}) : p.util.flow.noop)];

exports.inputMeta = (state0, p0, cb) => p0.util.flow.serial([
	() => ({program : "winedump"}),
	(state, p) =>
	{
		const winedumpMeta = p.util.program.getMeta(state, "winedump");
		if(winedumpMeta)
			state.input.meta[p.format.meta.formatid] = winedumpMeta;
		
		return p.util.flow.noop;
	}
])(state0, p0, cb);
