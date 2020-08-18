"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name        : "HiRes Player Missile",
	ext         : [".hpm"],
	filesize    : [19203],
	unsupported : true,
	notes       : XU.trim`
		Atari Graphics Studio is capable of converting these files. Sadly I ran into issues with it when running it under Wine with AutoIt.
		I haven't been able to locate another converter or any other real info for it.`
};

// These steps work when running under regular linux and wine, but fail when running in a virtual wine environment, not sure why
// Looks like at the last step where I want to 'save' the files, it's kinda messed up and doesn't see any files, so when trying to Save it just hangs
/*
exports.steps =
[
	(state, p) => p.util.wine.run({cmd : "AtariGraphicsStudio/ags.exe", args : state.input.filePath, cwd : state.cwd, autoItScript : `
		WinActivate("[CLASS:TMain_Form]", "")
		Sleep(500)
		Send("!f")
		Sleep(500)
		Send("o")
		Sleep(500)
		Send("{ENTER}")
		Sleep(500)
		Send("${path.join(state.cwd, state.input.filePath).replaceAll(path.sep, "\\")}")
		Sleep(500)
		Send("{ENTER}")
		Sleep(3000)
		Send("!f")
		Sleep(500)
		Send("e")
		Sleep(500)
		Send("{ENTER}")
		Sleep(500)
		Send("outfile")
		Sleep(1000)
		Send("{TAB}")
		Sleep(1000)
		Send("p")
		Sleep(1000)
		Send("{TAB}")
		Sleep(1000)
		Send("{ENTER}")
		Sleep(3000)
		Send("!f")
		Sleep(500)
		Send("e")
		Sleep(500)
		Send("e")
		Sleep(500)
		Send("{ENTER}")`}),
	(state, p) => p.util.file.move(path.join(state.cwd, "outfile.png"), path.join(state.output.absolute, `${state.input.name}.png`))
];
*/
