"use strict";
const XU = require("@sembiance/xu"),
	fs = require("fs");

exports.meta =
{
	name     : "Blazing Paddles",
	website  : "http://fileformats.archiveteam.org/wiki/Blazing_Paddles",
	ext      : [".pi"],
	mimeType : "image/x-blazing-paddles"
};

// Blazing Paddles .pi files are either 10240 or 10242 bytes in length
// https://www.luigidifraia.com/c64/bmp2koala/help/Blazing.html
exports.custom = state => ([10240, 10242].includes(fs.statSync(state.input.absolute).size));

exports.converterPriorty = ["nconvert", "recoil2png", "abydosconvert"];
