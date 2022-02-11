import {Format} from "../../Format.js";
import {_PNG_MAGIC} from "./png.js";
import {_JPG_MAGIC} from "./jpg.js";

export class doodleC64 extends Format
{
	name           = "Doodle C64";
	website        = "http://fileformats.archiveteam.org/wiki/Doodle!_(C64)";
	ext            = [".dd", ".jj"];
	magic          = ["Doodle bitmap (compressed)"];
	fileSize       = {".dd" : [9218, 9026, 9346]};
	matchFileSize  = true;
	forbiddenMagic = [..._PNG_MAGIC, ..._JPG_MAGIC];
	converters     = ["recoil2png", "nconvert"];
}
