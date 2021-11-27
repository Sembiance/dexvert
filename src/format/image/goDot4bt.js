import {Format} from "../../Format.js";

export class goDot4bt extends Format
{
	name           = "GoDot 4Bit Image";
	website        = "http://fileformats.archiveteam.org/wiki/GoDot";
	ext            = [".4bt", ".clp"];
	forbidExtMatch = [".clp"];
	magic          = ["GoDot 4-bit graphics bitmap"];
	converters     = ["recoil2png", "nconvert", "view64"]
}
