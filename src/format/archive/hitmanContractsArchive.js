import {Format} from "../../Format.js";

export class hitmanContractsArchive extends Format
{
	name           = "Hitman Contracts Archive";
	ext            = [".prm", ".tex"];
	forbidExtMatch = true;
	magic          = ["dragon: HMCPRM "];
	weakMagic      = true;
	converters     = ["dragonUnpacker[types:HMCPRM]"];
}
