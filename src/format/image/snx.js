import {Format} from "../../Format.js";

export class snx extends Format
{
	name       = "Second Nature Screensaver Graphic";
	website    = "http://fileformats.archiveteam.org/wiki/Second_Nature_Screensaver_Graphic";
	ext        = [".snx"];
	notes      = "This only is able to convert files that are just wrapped JPEG images (dragon*.snx). Others are in an unknown file format, including barw22.snx.";
	converters = ["deark[module:jpegscan]"];	// foremost and irfanView also work, but not any better/faster than deark
}
