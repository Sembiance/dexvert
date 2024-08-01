import {Format} from "../../Format.js";

export class pabxBackground extends Format
{
	name           = "PABX Background";
	website        = "http://fileformats.archiveteam.org/wiki/PABX_background";
	ext            = [".pix"];
	forbidExtMatch = true;
	magic          = ["PABX Background bitmap"];
	weakMagic      = true;
	converters     = ["nconvert"];
}
