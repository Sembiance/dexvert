import {Format} from "../../Format.js";

export class moduleDescriptionFile extends Format
{
	name           = "Module Description File";
	website        = "https://www.cubic.org/player/doc/node73.htm";
	ext            = [".mdz"];
	forbidExtMatch = true;
	magic          = ["Open Cubic Player Module Information MDZ"];
	untouched      = true;
	metaProvider   = ["text"];
}
