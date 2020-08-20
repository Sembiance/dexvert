"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	name  : "Disney Animation Studio CFAST",
	ext   : [".cft"],
	magic : ["CFast Animation"],
	notes : XU.trim`
		FLICK.EXE just loops the video forever, haven't figured out a way to get it to stop after playing once. So I just record for 40 seconds and that's the result.
		Due to just running DOSbox and recording the screen, there is dosbox logo at the start.
		Finally, the format is documented, so someone could create a more modern converter.`
};

exports.steps =
[
	(state, p) => p.util.dos.run({p, state,
		bin      : "FLICK.EXE",
		autoExec : [`FLICK.EXE -qa ${state.input.filePath}`],
		timeout  : XU.SECOND*40,
		video    : path.join(state.output.absolute, `${state.input.name}.mp4`)})
];
