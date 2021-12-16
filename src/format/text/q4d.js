import {Format} from "../../Format.js";

export class q4d extends Format
{
	name           = "XLD4 Data Document";
	website        = "http://fileformats.archiveteam.org/wiki/XLD4";
	ext            = [".q4d"];
	forbidExtMatch = true;
	magic          = ["XLD4 Graphic Data Document bitmap"];
	charSet        = "IBM-943";
	untouched      = true;
	metaProvider   = ["text"];
}
