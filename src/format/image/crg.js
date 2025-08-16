import {Format} from "../../Format.js";

export class crg extends Format
{
	name       = "Calamus Raster Graphic";
	website    = "http://fileformats.archiveteam.org/wiki/Calamus_Raster_Graphic";
	ext        = [".crg"];
	magic      = ["Calamus Raster Graphic bitmap", "deark: crg", "Calamus :crg:"];
	converters = ["recoil2png", "deark[module:crg]", "nconvert[format:crg]", "wuimg[matchType:magic]"];
}
