/*
import {Format} from "../../Format.js";

export class eps extends Format
{
	name = "Encapsulated PostScript";
	website = "http://fileformats.archiveteam.org/wiki/EPS";
	ext = [".eps",".epsf",".epsi",".epi",".ept"];
	mimeType = "application/postscript";
	magic = ["Encapsulated PostScript File Format",{},"Encapsulated PostScript binary","DOS EPS Binary File Postscript"];
	notes = "\nSometimes it's a vector based image, sometimes not. Haven't determined a way to differeentiate.\nSo we just convert to PNG with nconvert and also to SVG with inkscape.";

steps = [null,null];
}
*/
/*
"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name     : "Encapsulated PostScript",
	website  : "http://fileformats.archiveteam.org/wiki/EPS",
	ext      : [".eps", ".epsf", ".epsi", ".epi", ".ept"],
	mimeType : "application/postscript",
	magic    : ["Encapsulated PostScript File Format", /^PostScript document.*type EPS/, "Encapsulated PostScript binary", "DOS EPS Binary File Postscript"],
	notes    : XU.trim`
		Sometimes it's a vector based image, sometimes not. Haven't determined a way to differeentiate.
		So we just convert to PNG with nconvert and also to SVG with inkscape.`
};

exports.steps = [
	() => ({program : "nconvert"}),
	() => ({program : "inkscape"})	// convert can also convert EPS to SVG, but it does a pretty poor job most of the time
];

*/
