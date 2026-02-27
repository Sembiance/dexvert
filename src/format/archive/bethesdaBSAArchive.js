import {Format} from "../../Format.js";

export class bethesdaBSAArchive extends Format
{
	name           = "Bethesda BSA Archive";
	ext            = [".bsa"];
	forbidExtMatch = true;
	magic          = ["dragon: BSA "];
	converters     = ["dragonUnpacker[types:BSA]"];
}
