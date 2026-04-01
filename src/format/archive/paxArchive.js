import {Format} from "../../Format.js";

export class paxArchive extends Format
{
	name           = "Pax Archive";
	ext            = [".pax"];
	forbidExtMatch = true;
	magic          = ["Pax compressed archive", "Atari LZF0 compressed archive"];
	converters     = ["vibeExtract"];
}
