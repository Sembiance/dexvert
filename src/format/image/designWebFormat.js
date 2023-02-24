import {Format} from "../../Format.js";

export class designWebFormat extends Format
{
	name        = "Design Web Format";
	website    = "http://fileformats.archiveteam.org/wiki/DWF";
	ext        = [".dwf", ".dwfx"];
	magic      = ["Autodesk Design Web Format", /^x-fmt\/49( |$)/];
	converters = ["viewCompanion", "dwg2bmp", "canvas[matchType:magic][nonRaster]"];
}
