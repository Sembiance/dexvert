import {Format} from "../../Format.js";

export class moduleDescriptionFile extends Format
{
	name           = "Module Description File";
	website        = "http://fileformats.archiveteam.org/wiki/MDZ";
	ext            = [".mdz"];
	forbidExtMatch = true;
	magic          = ["Open Cubic Player Module Information MDZ"];
	untouched      = true;
	metaProvider   = ["text"];
}
