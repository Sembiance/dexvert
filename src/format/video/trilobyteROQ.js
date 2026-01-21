import {Format} from "../../Format.js";

export class trilobyteROQ extends Format
{
	name           = "Trilobyte ROQ";
	ext            = [".roq"];
	forbidExtMatch = true;
	magic          = ["Trilobyte GDJ/VDX"];
	weakMagic      = true;
	converters     = ["na_game_tool[format:roq]"];
}
