"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name                : "Electronika BK PIC",
	ext                 : [".pic"],
	fileSize            : 16384,
	forbidFileSizeMatch : true	// Format too obscure to be matching on the fileSize
};

exports.converterPriorty = ["recoil2png"];
