import {Format} from "../../Format.js";

export class warc extends Format
{
	name           = "WARC Archive";
	website        = "http://fileformats.archiveteam.org/wiki/WARC";
	ext            = [".warc"];
	forbidExtMatch = true;
	magic          = ["WARC Archive version", "Web ARChive File Format", /^WARC$/, /^fmt\/1355( |$)/];
	converters     = ["Warcat"];
}
