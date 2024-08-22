import {Format} from "../../Format.js";

export class cavewarsSounds extends Format
{
	name           = "Cavewar Sounds";
	ext            = [".dbs"];
	forbidExtMatch = true;
	magic          = ["Cavewars sounds archive"];
	weakMagic      = true;
	converters     = ["foremost -> sox"];
}
