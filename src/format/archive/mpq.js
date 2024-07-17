import {Format} from "../../Format.js";

export class mpq extends Format
{
	name           = "MoPaQ Archive";
	ext            = [".mpq"];
	magic          = ["MoPaQ (MPQ) archive", "MPQ Archive", "Archive: MPQ"];
	forbiddenMagic = ["StarCraft Map"];
	unsupported    = true;
	notes          = "Need some sample archives. Can use this to extract: https://github.com/Kanma/MPQExtractor or https://github.com/uakfdotb/umpqx";
}
