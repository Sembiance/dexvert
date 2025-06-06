import {Format} from "../../Format.js";

export class portfolioGraphics extends Format
{
	name       = "Portfolio Graphics";
	website    = "http://fileformats.archiveteam.org/wiki/PGF_(Portfolio_Graphics)";
	ext        = [".pgf"];
	magic      = ["deark: pf_pgf (PGF (Portfolio graphics))", "Portfolio Graphic Compressed :pgf:"];
	fileSize   = 1920;
	converters = ["deark[module:pf_pgf]", "recoil2png", "nconvert[format:pgf]"];
}
