import {Format} from "../../Format.js";

export class europaArchive extends Format
{
	name           = "Europa Archive";
	ext            = [".pak"];
	forbidExtMatch = true;
	magic          = ["dragon: Europa "];
	converters     = ["dragonUnpacker[types:Europa]"];
}
