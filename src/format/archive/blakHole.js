import {Format} from "../../Format.js";

export class blakHole extends Format
{
	name           = "BlakHole Archive";
	ext            = [".bh"];
	forbidExtMatch = true;
	magic          = ["BlackHole compressed archive", /^BlakHole archive data/];
	converters     = ["izArc"];
}
