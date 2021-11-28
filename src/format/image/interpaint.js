import {Format} from "../../Format.js";

export class interpaint extends Format
{
	name           = "Interpaint";
	website        = "http://fileformats.archiveteam.org/wiki/Interpaint";
	ext            = [".iph", ".ipt", ".lre", ".hre"];
	forbidExtMatch = true;
	magic          = ["Interpaint bitmap"];
	weakMagic      = true;
	converters     = ["recoil2png", "nconvert", "view64"];
}
