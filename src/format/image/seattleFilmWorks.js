"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name           : "Seattle FilmWorks/PhotoWorks PhotoMail",
	website        : "http://fileformats.archiveteam.org/wiki/Seattle_FilmWorks",
	ext            : [".sfw", ".pwp", ".pwm", ".alb"],
	magic          : ["Seattle FilmWorks"],
	mimeType       : "image/x-seattle-filmworks"
};

exports.converterPriority = ["convert", "abydosconvert", "nconvert"];
