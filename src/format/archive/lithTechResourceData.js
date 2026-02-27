import {Format} from "../../Format.js";

export class lithTechResourceData extends Format
{
	name           = "LithTech Resource data";
	ext            = [".rez"];
	forbidExtMatch = true;
	magic          = ["LithTech Resource data", /^geArchive: REZ_REZMGR( |$)/, "dragon: REZ "];
	converters     = ["gameextractor[codes:REZ_REZMGR]", "dragonUnpacker[types:REZ]"];
}
