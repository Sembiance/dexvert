"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "Windows Screensaver",
	ext            : [".scr"],
	forbidExtMatch : true,
	magic          : ["Windows New Executable", "MS-DOS executable, NE for MS Windows 3.x", "Win16 NE executable"],
	weakMagic      : true,
	unsupported    : true,
	highConfidence : true,
	notes          : "I could convert these to a video by running them with `wine <file.scr> /s` however that's not very safe and I don't feel like bothering to sandbox wine."
};

//exports.wine = state => path.relative(path.resolve(path.join(__dirname, "..", "..", "..", "wine")), state.input.absolute);
//exports.wineOptions = state => ({timeout : XU.SECOND*10, recordVideo : path.join(undefined, "test.mp4"});
//exports.args = (state, p, r) => (["/s"]);	// eslint-disable-line no-unused-vars
