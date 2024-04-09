import {Format} from "../../Format.js";

export class musicProTracker extends Format
{
	name         = "Music ProTracker";
	website      = "http://atariki.krap.pl/index.php/MPT_%28format_pliku%29";
	ext          = [".mpt"];
	magic        = ["Music ProTracker"];
	metaProvider = ["musicInfo"];
	converters   = ["asapconv"];
}
