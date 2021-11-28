import {Format} from "../../Format.js";

export class eps extends Format
{
	name       = "Encapsulated PostScript";
	website    = "http://fileformats.archiveteam.org/wiki/EPS";
	ext        = [".eps", ".epsf", ".epsi", ".epi", ".ept"];
	mimeType   = "application/postscript";
	magic      = ["Encapsulated PostScript File Format", /^PostScript document.*type EPS/, "Encapsulated PostScript binary", "DOS EPS Binary File Postscript"];
	notes      = "Sometimes it's a vector based image, sometimes not. Haven't determined a way to differentiate. So we just convert to PNG with nconvert and also to SVG with inkscape.";
	converters = ["nconvert & inkscape"];
}
