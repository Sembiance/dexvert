"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Disney Animation Studio CFAST",
	website : "http://justsolve.archiveteam.org/wiki/CFAST_Disney_Animation_Studio",
	ext     : [".cft"],
	magic   : ["CFast Animation"],
	notes   : XU.trim`
		FLICK.EXE just loops the video forever, haven't figured out a way to get it to stop after playing once. So I just record for 40 seconds and that's the result.
		Due to just running DOSbox and recording the screen, there is dosbox logo at the start.
		Finally, the format is documented, so someone could create a more modern converter.`
};

exports.converterPriority = ["flick"];
