import {Format} from "../../Format.js";

export class cdxl extends Format
{
	name         = "CDXL";
	website      = "http://fileformats.archiveteam.org/wiki/CDXL";
	ext          = [".cdxl", ".xl"];
	magic        = ["Amiga CDXL video", "Commodore CDXL video (cdxl)"];
	metaProvider = ["mplayer"];
	converters   = ["ffmpeg[format:cdxl]"];
}
