import {Format} from "../../Format.js";

export class crg extends Format
{
	name       = "Calamus Raster Graphic";
	website    = "http://fileformats.archiveteam.org/wiki/Calamus_Raster_Graphic";
	ext        = [".crg"];
	magic      = ["Calamus Raster Graphic bitmap"];
	converters = ["recoil2png", "deark[module:crg]", "nconvert"];
}
