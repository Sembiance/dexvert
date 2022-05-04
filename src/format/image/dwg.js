import {Format} from "../../Format.js";

export class dwg extends Format
{
	name       = "AutoCAD Drawing";
	website    = "http://fileformats.archiveteam.org/wiki/DWG";
	ext        = [".dwg", ".dwt"];
	magic      = [/^AutoCAD R.+ Drawing/, "DWG AutoDesk AutoCAD", /^fmt\/(30|31|32|531)( |$)/];
	converters = ["totalCADConverterX[outType:pdf] -> pdf2svg", "dwg2SVG", "dwg2bmp", "uniconvertor", "irfanView", "nconvert", "corelPhotoPaint", "canvas[matchType:magic][nonRaster]"];
}
