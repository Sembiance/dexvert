"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Blazing Paddles",
	website  : "http://fileformats.archiveteam.org/wiki/Blazing_Paddles",
	ext      : [".pi"],
	mimeType : "image/x-blazing-paddles",
	// https://www.luigidifraia.com/c64/bmp2koala/help/Blazing.html
	fileSize : [10240, 10242]
};

exports.converterPriorty = ["recoil2png", "nconvert", "abydosconvert", "view64"];
