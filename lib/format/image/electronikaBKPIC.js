"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name                : "Electronika BK PIC",
	ext                 : [".pic"],
	filesize            : [16384],
	forbidFilesizeMatch : true	// Format too obscure to be matching on the filesize
};

exports.converterPriorty = ["recoil2png"];
