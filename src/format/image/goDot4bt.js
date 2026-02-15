import {Format} from "../../Format.js";

export class goDot4bt extends Format
{
	name       = "GoDot 4Bit Image";
	website    = "http://fileformats.archiveteam.org/wiki/GoDot";
	ext        = [".4bt"];
	magic      = ["GoDot 4-bit graphics bitmap", "GoDot :god:", /^fmt\/1834( |$)/];
	converters = ["recoil2png[format:4BT]", "nconvert[format:god]", "view64"];
}
