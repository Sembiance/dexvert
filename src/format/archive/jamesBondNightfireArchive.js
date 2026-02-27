import {Format} from "../../Format.js";

export class jamesBondNightfireArchive extends Format
{
	name           = "James Bond Nightfire 007 Archive";
	ext            = [".007"];
	forbidExtMatch = true;
	magic          = ["dragon: 007 "];
	converters     = ["dragonUnpacker[types:007]"];
}
