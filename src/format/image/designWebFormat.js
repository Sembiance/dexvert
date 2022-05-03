import {Format} from "../../Format.js";

export class designWebFormat extends Format
{
	name        = "Design Web Format";
	website    = "http://fileformats.archiveteam.org/wiki/DWF";
	ext        = [".dwf", ".dwfx"];
	magic      = ["Autodesk Design Web Format"];
	converters = ["totalCADConverterX[outType:pdf] -> pdf2svg", "dwg2bmp", "canvas[matchType:magic][nonRaster]"];
}
