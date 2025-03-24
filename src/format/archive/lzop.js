import {Format} from "../../Format.js";

export class lzop extends Format
{
	name           = "LZOP Archive";
	website        = "http://fileformats.archiveteam.org/wiki/Lzop";
	ext            = [".lzo"];
	forbidExtMatch = true;
	magic          = ["lzop compressed", "LZO Archiv gefunden", "Archive: LZOP compressed data", "LZO compressed data", "application/x-lzop", /^lzop compressed data/];
	converters     = ["lzop"];
}
