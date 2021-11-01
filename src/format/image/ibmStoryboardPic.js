"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "IBM Storyboard PIC",
	website        : "https://winworldpc.com/product/ibm-storyboard/live-20",
	ext            : [".pic", ".cap"],
	forbiddenExt   : [".txm"],
	forbidExtMatch : true,
	magic          : ["IBM Storyboard bitmap", "IBM Storyboard screen Capture"],
	notes          : XU.trim`
		Unable to use SBLIVE/PICTYPE.EXE to determine if it's valid due to that program not working with shell redirection (see sandbox/legacy/programs_and_formats/storyboardLivePicType.js)
		Several encountered .PIC files that PICTYPE does say are valid don't show in SHOWPIC.EXE for whatever reason.`
};

exports.converterPriority = ["storyboardLiveShowPic"];
