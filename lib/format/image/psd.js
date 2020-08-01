"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Adobe Photoshop",
	website  : "http://fileformats.archiveteam.org/wiki/PSD",
	ext      : [".psd"],
	mimeType : "image/vnd.adobe.photoshop",
	magic    : [/^Adobe Photoshop [Ii]mage/, /^Adobe Photoshop$/]
};

exports.converterPriorty = ["convert"];

// I made the decision above to just use regular convert, which will extract all layers from the PSD.
// I could in theory just extract the 'main' image by doing:
// exports.steps = [ (state, p) => ({program : "convert", args : [`${state.input.filePath}[0]`, ...p.program.convert.STRIP_ARGS, path.join(state.output.dirPath, `outfile${state.convertExt || ".png"}`)]}) ];
