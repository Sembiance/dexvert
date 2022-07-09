import {Format} from "../../Format.js";

export class mikeDavies extends Format
{
	name         = "Mike Davies Module";
	website      = "http://fileformats.archiveteam.org/wiki/Mike_Davies";
	ext          = [".md"];
	magic        = ["Mike Davies module"];
	metaProvider = ["musicInfo"];
	converters   = ["uade123"];
}
