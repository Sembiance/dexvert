import {Format} from "../../Format.js";

export class iavfVideoArchive extends Format
{
	name           = "IAVF video Archive";
	ext            = [".avi", ".tsh"];
	forbidExtMatch = true;
	magic          = ["IAVF video"];
	converters     = ["na_game_tool_extract[format:iavf]"];
}
