import {Format} from "../../Format.js";

export class macBinary extends Format
{
	name           = "MacBinary";
	website        = "http://fileformats.archiveteam.org/wiki/MacBinary";
	magic          = ["MacBinary 2", "MacBinary II"];
	ext            = [".bin"];
	forbidExtMatch = true;
	fallback       = true;
	converters     = ["deark"]
}