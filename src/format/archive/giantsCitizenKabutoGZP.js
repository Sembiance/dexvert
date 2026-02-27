import {Format} from "../../Format.js";

export class giantsCitizenKabutoGZP extends Format
{
	name           = "Giants Citizen Kabuto GZP Archive";
	ext            = [".gzp"];
	forbidExtMatch = true;
	magic          = [/^geArchive: GZP( |$)/, "dragon: GZP "];
	converters     = ["gameextractor[codes:GZP]", "dragonUnpacker[types:GZP]"];
}
