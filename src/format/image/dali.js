import {Format} from "../../Format.js";

export class dali extends Format
{
	name           = "Dali";
	website        = "http://fileformats.archiveteam.org/wiki/Dali";
	ext            = [".sd0", ".sd1", ".sd2", ".hpk", ".lpk", ".mpk"];
	fileSize       = {".sd0,.sd1,.sd2" : 32128};
	matchFileSize  = true;
	converters     = ["recoil2png", "nconvert", "wuimg"];
}
