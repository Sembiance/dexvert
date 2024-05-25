import {Format} from "../../Format.js";

export class dwg extends Format
{
	name       = "AutoCAD Drawing";
	website    = "http://fileformats.archiveteam.org/wiki/DWG";
	ext        = [".dwg", ".dwt"];
	magic      = ["Archive: AutoCAD Drawing", /^AutoCAD .*Drawing/, "DWG AutoDesk AutoCAD", /^fmt\/(22|24|25|26|27|28|29|30|31|32|531)( |$)/];
	converters = ["dwg2SVG", "dwg2bmp", "uniconvertor", "irfanView", "nconvert", "corelPhotoPaint", "canvas[matchType:magic][nonRaster]"];
}
