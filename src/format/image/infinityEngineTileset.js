import {Format} from "../../Format.js";

export class infinityEngineTileset extends Format
{
	name           = "Infinity Engine Tileset";
	ext            = [".tis", ".tiz"];
	forbidExtMatch = true;
	magic          = ["Infinity Engine tileset", "Infinity Engine Tileset (Compressed)", "Infinity Engine compressed Tileset"];
	converters     = ["vibeExtract[skipVerify]"];
}

