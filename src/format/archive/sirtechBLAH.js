import {Format} from "../../Format.js";

export class sirtechBLAH extends Format
{
	name           = "Sirtech BLAH";
	ext            = [".sms", ".smk"];
	forbidExtMatch = true;
	magic          = ["Sirtech BLAH"];
	converters     = ["na_game_tool_extract[format:blah]"];
}

