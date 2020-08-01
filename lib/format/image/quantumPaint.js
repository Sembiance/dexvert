"use strict";
const XU = require("@sembiance/xu");
exports.meta =
{
	name     : "Quantum Paint",
	website  : "http://fileformats.archiveteam.org/wiki/QuantumPaint",
	ext      : [".pbx"],
	mimeType : "image/x-quantum-paint"
};

exports.converterPriorty = ["recoil2png", "abydosconvert"];
