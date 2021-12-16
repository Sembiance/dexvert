import {Format} from "../../Format.js";
import {TEXT_MAGIC} from "../../Detection.js";

export class bas extends Format
{
	name           = "BASIC Source File";
	website        = "http://fileformats.archiveteam.org/wiki/BASIC";
	ext            = [".bas"];
	forbidExtMatch = true;
	magic          = TEXT_MAGIC;
	weakMagic      = true;
	untouched      = true;
	metaProvider   = ["text"];
}
