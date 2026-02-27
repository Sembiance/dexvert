import {Format} from "../../Format.js";

export class sinArchive extends Format
{
	name           = "Sin Archive";
	ext            = [".sin"];
	forbidExtMatch = true;
	magic          = ["dragon: SIN "];
	converters     = ["dragonUnpacker[types:SIN]"];
}
