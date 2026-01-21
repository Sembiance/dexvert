import {Format} from "../../Format.js";

export class microidsGRN extends Format
{
	name           = "Microids GRN Video";
	ext            = [".grn"];
	forbidExtMatch = true;
	magic          = ["Microids GRN Video"];
	weakMagic      = true;
	converters     = ["na_game_tool[format:grn]"];
	unsupported    = true;	// Could not locate any sample files. If find some, add to dexmagic: "Microids GRN Video"					   : [{offset : 0, match : "ANIM"}],
}
