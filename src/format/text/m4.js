import {Format} from "../../Format.js";

export class m4 extends Format
{
	name           = "M4 Source File";
	website        = "http://fileformats.archiveteam.org/wiki/M4";
	ext            = [".m4"];
	forbidExtMatch = true;
	magic          = ["m4 preprocessor / macro source", "M4 macro processor script"];
	weakMagic      = true;
	untouched      = true;
	metaProvider   = ["text"];
}
