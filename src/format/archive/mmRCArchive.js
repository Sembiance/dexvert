import {Format} from "../../Format.js";

export class mmRCArchive extends Format
{
	name           = "MMRC Archive";
	ext            = [".mrc"];
	forbidExtMatch = true;
	magic          = ["Generic RIFF file mmRC", "dragon: mmRC "];
	converters     = ["dragonUnpacker[types:mmRC]"];
}
