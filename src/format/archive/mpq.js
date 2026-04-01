import {Format} from "../../Format.js";

export class mpq extends Format
{
	name           = "MoPaQ Archive";
	ext            = [".mpq"];
	magic          = ["MoPaQ (MPQ) archive", "MPQ Archive", "Archive: MPQ"];
	forbiddenMagic = ["StarCraft Map"];
	converters     = ["vibeExtract"];
}
