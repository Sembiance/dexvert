"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	name  : "Fantavision Movie",
	ext   : [".mve"],
	magic : ["Fantavision Movie"],
	notes : XU.trim`
		PLAYER.EXE just loops the video forever, haven't figured out a way to get it to stop after playing once. So I just record for 1 minute and that's the result.
		Also, there is sound effects but my runUtil Xvfb doesn't support sound recording yet, so no sound.
		Lastly, I just cheat by running DOSbox and recording the screen, so there is dosbox video at the start heh.`
};

exports.steps =
[
	(state, p) => p.util.dos.run({p, state,
		subdir   : "FANTAVSN",
		autoExec : [`COPY ${state.input.filePath.toUpperCase()} FANTAVSN\\F.MVE`, "CD FANTAVSN", `PLAYER.EXE`],
		timeout  : XU.MINUTE,
		video    : path.join(state.output.absolute, `${state.input.name}.mp4`)})
];
