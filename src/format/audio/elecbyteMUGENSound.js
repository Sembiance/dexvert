import {Format} from "../../Format.js";

export class elecbyteMUGENSound extends Format
{
	name           = "Elecbyte M.U.G.E.N. Sound";
	ext            = [".snd"];
	forbidExtMatch = true;
	magic          = ["Elecbyte M.U.G.E.N. sound"];
	converters     = ["vibe2wav"];
}
