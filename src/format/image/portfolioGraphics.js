import {Format} from "../../Format.js";

export class portfolioGraphics extends Format
{
	name       = "Portfolio Graphics";
	website    = "http://fileformats.archiveteam.org/wiki/PGF_(Portfolio_Graphics)";
	ext        = [".pgf"];
	fileSize   = 1920;
	converters = ["recoil2png"];
}
