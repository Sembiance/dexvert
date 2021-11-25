import {Format} from "../../Format.js";

export class wmf extends Format
{
	name       = "Microsoft Windows Metafile";
	website    = "http://fileformats.archiveteam.org/wiki/WMF";
	ext        = [".wmf", ".apm", ".wmz"];
	mimeType   = "image/wmf";
	magic      = [{}];
	notes      = "Some WMF files like 001.WMF just have an embedded PNG. So the initial programs that convert to SVG will fail, and fall back to convert which will produce a PNG.";
	converters = ["wmf2svg", "uniconvertor", {"program":"soffice","flags":{"sofficeType":"svg"}},"convert"]

metaProviders = [""];
}

/*
"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Microsoft Windows Metafile",
	website  : "http://fileformats.archiveteam.org/wiki/WMF",
	ext      : [".wmf", ".apm", ".wmz"],
	mimeType : "image/wmf",
	magic    : [/^Windows [Mm]etafile/],
	notes    : "Some WMF files like 001.WMF just have an embedded PNG. So the initial programs that convert to SVG will fail, and fall back to convert which will produce a PNG."
};

exports.converterPriority = ["wmf2svg", "uniconvertor", {program : "soffice", flags : {sofficeType : "svg"}}, "convert"];

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

*/
