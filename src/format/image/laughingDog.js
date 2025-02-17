import {Format} from "../../Format.js";

export class laughingDog extends Format
{
	name           = "Laughing Dog Screen Maker";
	website        = "http://justsolve.archiveteam.org/wiki/Laughing_Dog_Screen_Maker";
	ext            = [".dog"];
	forbidExtMatch = true;
	magic          = [/^Laughing Dog$/];
	weakMagic      = true;
	converters     = ["laughingDog"];
}
