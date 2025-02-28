import {Format} from "../../Format.js";

export class balkoUFLGameDataArchive extends Format
{
	name           = "Balko UFL game data archive";
	ext            = [".laf", ".ufl"];
	forbidExtMatch = true;
	magic          = ["Balko UFL game data archive"];
	weakMagic      = true;
	converters     = ["foremost"];
}
