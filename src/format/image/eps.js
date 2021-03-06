"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Encapsulated PostScript",
	website  : "http://fileformats.archiveteam.org/wiki/EPS",
	ext      : [".eps", ".epsf", ".epsi", ".epi", ".ept"],
	mimeType : "application/postscript",
	magic    : ["Encapsulated PostScript File Format", /^PostScript document.*type EPS/],
	notes    : XU.trim`
		Sometimes it's a vector based image, sometimes not. Haven't determined a way to differeentiate.
		So we just convert to PNG with nconvert and also to SVG with inkscape.`
};

exports.steps = [
	() => ({program : "nconvert"}),
	() => ({program : "inkscape"})	// convert can also convert EPS to SVG, but it does a pretty poor job most of the time
];
