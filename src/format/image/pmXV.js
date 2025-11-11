import {Format} from "../../Format.js";

export class pmXV extends Format
{
	name           = "PM XV Bitmap";
	ext            = [".pm"];
	forbidExtMatch = true;
	magic          = ["PM XV bitmap", "deark: pm_xv", "PM :pm:"];
	weakMagic      = true;
	converters     = ["nconvert[format:pm]", "deark[module:pm_xv]"];
}
