"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Microsoft Windows Metafile",
	website  : "http://fileformats.archiveteam.org/wiki/WMF",
	ext      : [".wmf", ".apm", ".wmz"],
	mimeType : "image/wmf",
	magic    : [/^Windows [Mm]etafile/],
	notes    : "This is a vector format, but 'convert' doesn't support exporting it to svg. So if uniconvertor fails, we'll just get a PNG out instead of an SVG."
};

exports.converterPriorty = ["uniconvertor", "convert"];

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);
