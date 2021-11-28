import {Format} from "../../Format.js";

export class delmPaint extends Format
{
	name       = "DelmPaint";
	website    = "http://fileformats.archiveteam.org/wiki/Calamus_Raster_Graphic";
	ext        = [".del", ".dph"];
	converters = ["recoil2png"];
}
