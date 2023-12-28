import {Format} from "../../Format.js";

export class wmf extends Format
{
	name         = "Microsoft Windows Metafile";
	website      = "http://fileformats.archiveteam.org/wiki/Windows_Metafile";
	ext          = [".wmf", ".apm", ".wmz"];
	mimeType     = "image/wmf";
	magic        = [/^Windows [Mm]etafile/, "Aldus Placeable Metafile", /^x-fmt\/119( |$)/];
	notes        = "Some WMF files like 001.WMF just have an embedded PNG. So the initial programs that convert to SVG will fail, and fall back to convert which will produce a PNG.";
	metaProvider = ["image"];
	converters   = [
		"wmf2svg", "uniconvertor", "soffice[outType:svg]", "convert", "iio2png",
		"keyViewPro", "corelDRAW", "hiJaakExpress", "corelPhotoPaint", "picturePublisher", "canvas[matchType:magic][nonRaster]"
	];
}
