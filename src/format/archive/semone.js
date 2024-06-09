import {Format} from "../../Format.js";

export class semone extends Format
{
	name           = "SEMONE Archive";
	website        = "http://fileformats.archiveteam.org/wiki/SEMONE";
	ext            = [".one"];
	forbidExtMatch = true;
	magic          = ["SEMONE compressed archive", "SemOne archive data"];
	weakMagic      = true;
	converters     = ["semone"];
}
