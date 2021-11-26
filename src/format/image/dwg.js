import {Format} from "../../Format.js";

export class dwg extends Format
{
	name       = "AutoCAD Drawing";
	website    = "http://fileformats.archiveteam.org/wiki/DWG";
	ext        = [".dwg", ".dwt"];
	magic      = [/^AutoCAD R.+ Drawing/, "DWG AutoDesk AutoCAD"];
	converters = ["totalCADConverterX", "dwg2SVG", "dwg2bmp", "uniconvertor", "irfanView", "nconvert"]
}
