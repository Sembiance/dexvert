import {Format} from "../../Format.js";
import {_PNG_MAGIC} from "./png.js";
import {_JPG_MAGIC} from "./jpg.js";

export class imgScan extends Format
{
	name           = "IMG Scan";
	website        = "http://fileformats.archiveteam.org/wiki/IMG_Scan";
	ext            = [".rwl", ".raw", ".rwh"];
	fileSize       = {".rwl" : 64000, ".raw" : 128_000, ".rwh" : 256_000};
	matchFileSize  = true;
	forbiddenMagic = [..._PNG_MAGIC, ..._JPG_MAGIC];
	converters     = ["recoil2png"];
}
