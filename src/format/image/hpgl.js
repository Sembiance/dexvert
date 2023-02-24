import {Format} from "../../Format.js";

export class hpgl extends Format
{
	name       = "Hewlett-Packard Graphics Language";
	website    = "http://fileformats.archiveteam.org/wiki/HPGL";
	ext        = [".hpgl"];
	magic      = ["Hewlett-Packard Graphics Language"];
	converters = ["viewCompanion", "corelPhotoPaint", "canvas[matchType:magic][nonRaster]"];
}
