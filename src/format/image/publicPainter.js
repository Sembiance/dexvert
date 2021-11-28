import {Format} from "../../Format.js";

export class publicPainter extends Format
{
	name       = "Public  Painter";
	website    = "http://fileformats.archiveteam.org/wiki/Public_Painter";
	ext        = [".cmp"];
	converters = ["recoil2png"];
}
