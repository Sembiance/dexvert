import {Format} from "../../Format.js";

const _EPS_MAGIC = ["Encapsulated PostScript File Format", /^PostScript document.*type EPS/, "Encapsulated PostScript binary", "DOS EPS Binary File Postscript"];
const _EPS_EXT = [".eps", ".epsf", ".epsi", ".epi", ".ept"];
export {_EPS_MAGIC, _EPS_EXT};

export class eps extends Format
{
	name       = "Encapsulated PostScript";
	website    = "http://fileformats.archiveteam.org/wiki/EPS";
	ext        = _EPS_EXT;
	mimeType   = "application/eps";
	magic      = _EPS_MAGIC;
	notes      = "We used to convert to both PNG and SVG using nconvert & inkscape. But ps2pdf -> pdf2svg works much better and supports both raster and vector versions. Still, fallback to inkscape for some files like eagle and eagle.001";
	converters = ["ps2pdf -> pdf2svg", "inkscape", "gimp", "nconvert", "hiJaakExpress"];
}
