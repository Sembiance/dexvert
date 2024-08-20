import {Format} from "../../Format.js";

export class elecbyteMUGENSound extends Format
{
	name           = "Elecbyte M.U.G.E.N. Sound";
	ext            = [".snd"];
	forbidExtMatch = true;
	magic          = ["Elecbyte M.U.G.E.N. sound"];
	converters     = ["awaveStudio"];
	notes          = "awaveStudio doesn't reallly support this format, but it happens to produce some understandable output, but it messes up some parts for sure";
}
