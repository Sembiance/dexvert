import {Format} from "../../Format.js";

export class evaFont extends Format
{
	name           = "EVAfont";
	ext            = [".com"];
	forbidExtMatch = true;
	magic          = ["deark: evafont"];
	weakMagic      = true;
	converters     = ["deark[module:evafont][renameOut] -> deark[module:psf]"];
}
