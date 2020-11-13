"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	name  : "Fantavision Movie",
	ext   : [".mve"],
	magic : ["Fantavision Movie"],
	notes : XU.trim`
		PLAYER.EXE just loops the video forever, haven't figured out a way to get it to stop after playing once. So I just record for 40 seconds and that's the result.
		Also, there is sound effects but my runUtil Xvfb doesn't support sound recording yet, so no sound.
		I just run DOSbox and record the screen, so there is dosbox logo at the start.`
};

exports.steps =
[
	(state, p) => p.util.dos.run({state, p,
		subdir   : "FANTAVSN",
		autoExec : [`COPY ${state.input.filePath.toUpperCase()} FANTAVSN\\F.MVE`, "CD FANTAVSN", `PLAYER.EXE`],
		timeout  : XU.SECOND*40,
		video    : path.join(state.output.absolute, `${state.input.name}.mp4`)})
];
