import {Format} from "../../Format.js";

export class interPainter extends Format
{
	name       = "InterPainter";
	website    = "http://fileformats.archiveteam.org/wiki/InterPainter";
	ext        = [".inp", ".ins", ".int"];
	converters = ["recoil2png"];
}
