"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "NAPLPS Image",
	website        : "http://fileformats.archiveteam.org/wiki/NAPLPS",
	ext            : [".nap"],
	forbidExtMatch : true,
	magic          : ["NAPLPS graphics", "NAPLPS Image"],
	notes          : XU.trim`
		Some NAP files are actually animations. TURSHOW does actually show these, but sadly I can't detect this. So for now I treat all NAP files as just single images.
		
		There also exists .SCR files which are naplps Script files.
		The EAGMD.SCR file was created from using the P2NV02 program (can't locate anywhere, just a reference to it here: https://groups.google.com/g/alt.bbs/c/jFgKRCoBedA/m/zSW-AkORqIoJ?pli=1).
		My hunch is if I can find the P2NV02.ZIP archive, it probably has more info, maybe even a way to convert the SCR script back into an image.
		Note I learned a little bit about this format from README.EXE in eag2nap.zip`
};

exports.converterPriority = ["turshow"];
