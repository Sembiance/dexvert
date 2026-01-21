import {Format} from "../../Format.js";

export class hordeVDXArchive extends Format
{
	name           = "Horde VDX Archive";
	ext            = [".vdx"];
	forbidExtMatch = true;
	magic          = ["Horde VDX Archive"];
	converters     = ["na_game_tool_extract[format:horde-vdx]"];
}
