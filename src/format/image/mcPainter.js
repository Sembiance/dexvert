import {Format} from "../../Format.js";

export class mcPainter extends Format
{
	name       = "McPainter";
	website    = "http://fileformats.archiveteam.org/wiki/McPainter";
	ext        = [".mcp"];
	fileSize   = 16008;
	converters = ["recoil2png"];
}
