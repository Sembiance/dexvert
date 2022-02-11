import {Format} from "../../Format.js";
import {_PNG_MAGIC} from "./png.js";
import {_JPG_MAGIC} from "./jpg.js";

export class vzi extends Format
{
	name           = "VertiZontal Interlacing";
	website        = "http://fileformats.archiveteam.org/wiki/VertiZontal_Interlacing";
	ext            = [".vzi"];
	fileSize       = 16000;
	matchFileSize  = true;
	forbiddenMagic = [..._PNG_MAGIC, ..._JPG_MAGIC];
	converters     = ["recoil2png"];
}
