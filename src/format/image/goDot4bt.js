import {Format} from "../../Format.js";

export class goDot4bt extends Format
{
	name       = "GoDot 4Bit Image";
	website    = "http://fileformats.archiveteam.org/wiki/GoDot";
	ext        = [".4bt"];
	magic      = ["GoDot 4-bit graphics bitmap", /^fmt\/1834( |$)/];
	converters = ["recoil2png", "nconvert", "view64"];
}
