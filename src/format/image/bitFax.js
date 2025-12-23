import {Format} from "../../Format.js";

export class bitFax extends Format
{
	name           = "BitFax";
	ext            = [".bfx"];
	forbidExtMatch = true;
	magic          = ["BFX :bfx:", "BitFax Image"];
	converters     = ["nconvert[format:bfx]"];
}
