import {Format} from "../../Format.js";

export class php extends Format
{
	name           = "PHP Script";
	website        = "http://fileformats.archiveteam.org/wiki/PHP";
	ext            = [".php", ".phps"];
	forbidExtMatch = true;
	magic          = ["PHP source", "PHP script"];
	weakMagic      = true;
	untouched      = true;
	metaProvider   = ["text"];
}
