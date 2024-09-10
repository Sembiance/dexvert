import {Format} from "../../Format.js";

export class chiefLZArchive extends Format
{
	name       = "ChiefLZ LZA Archive";
	website    = "http://fileformats.archiveteam.org/wiki/ChiefLZ";
	ext        = [".lza", ".lzz"];
	magic      = ["LZA compressed archive", "LZA Archiv gefunden"];
	converters = ["lzaArchive"];
}
