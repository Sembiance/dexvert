import {Format} from "../../Format.js";

export class graphicWorkshopThumbnail extends Format
{
	name       = "Graphic Workship Thumbnail";
	website    = "http://fileformats.archiveteam.org/wiki/Graphic_Workshop_Thumbnail";
	ext        = [".thn"];
	magic      = ["Graphics Workshop for Windows Thumbnail", "deark: gws_thn", /^fmt\/336( |$)/];
	fileSize   = 9480;
	converters = ["deark[module:gws_thn]"];
}
