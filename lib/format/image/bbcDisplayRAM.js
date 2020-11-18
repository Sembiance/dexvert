"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name                : "BBC Display RAM Dump",
	fileSize            : 1000,
	mimeType            : "image/x-bbc-micro-screendump",
	forbidFileSizeMatch : true	// Format too obscure to be matching on the fileSize
};

exports.converterPriorty = ["abydosconvert"];
