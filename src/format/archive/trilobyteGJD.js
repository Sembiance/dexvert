import {Format} from "../../Format.js";

export class trilobyteGJD extends Format
{
	name           = "Trilobyte GJD Archive";
	ext            = [".gjd"];
	forbidExtMatch = true;
	magic          = ["Trilobyte GDJ/VDX"];
	weakMagic      = true;
	converters     = ["na_game_tool_extract[format:gjd]"];
}
