import {Format} from "../../Format.js";

export class pabxBackground extends Format
{
	name           = "PABX Background";
	website        = "http://fileformats.archiveteam.org/wiki/PABX_background";
	ext            = [".pix"];
	forbidExtMatch = true;
	magic          = ["PABX Background bitmap", "PABX background :pabx:"];
	weakMagic      = true;
	converters     = ["nconvert[format:pabx]"];
}
