import {Format} from "../../Format.js";

export class elecbyteMUGENSprites extends Format
{
	name           = "Elecbyte M.U.G.E.N. sprites";
	ext            = [".sff"];
	forbidExtMatch = true;
	magic          = ["Elecbyte M.U.G.E.N. sprites"];
	converters     = ["wuimg"];
}
