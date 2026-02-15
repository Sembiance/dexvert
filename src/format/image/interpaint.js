import {Format} from "../../Format.js";

export class interpaint extends Format
{
	name           = "Interpaint";
	website        = "http://fileformats.archiveteam.org/wiki/Interpaint";
	ext            = [".iph", ".ipt", ".lre", ".hre"];
	forbidExtMatch = true;
	magic          = ["Interpaint bitmap", "Interpaint (Hires) :ciph:", "InterPaint Multicolor :cipt:"];
	weakMagic      = true;
	converters     = ["recoil2png[format:IPT,IPH]", "nconvert[format:ciph]", "nconvert[format:cipt]", "view64"];
}
