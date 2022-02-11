import {Format} from "../../Format.js";
import {_PNG_MAGIC} from "./png.js";
import {_JPG_MAGIC} from "./jpg.js";

export class dali extends Format
{
	name           = "Dali";
	website        = "http://fileformats.archiveteam.org/wiki/Dali";
	ext            = [".sd0", ".sd1", ".sd2", ".hpk", ".lpk", ".mpk"];
	fileSize       = {".sd0,.sd1,.sd2" : 32128};
	matchFileSize  = true;
	forbiddenMagic = [..._PNG_MAGIC, ..._JPG_MAGIC];
	converters     = ["recoil2png", "nconvert"];
}
