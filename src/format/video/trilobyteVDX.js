import {Format} from "../../Format.js";

export class trilobyteVDX extends Format
{
	name           = "Trilobyte VDX";
	website        = "https://wiki.multimedia.cx/index.php/VDX";
	ext            = [".vdx"];
	forbidExtMatch = true;
	magic          = ["Trilobyte GDJ/VDX"];
	weakMagic      = true;
	converters     = ["na_game_tool[format:vdx]"];
}
