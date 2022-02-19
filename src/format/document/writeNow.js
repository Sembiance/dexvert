import {Format} from "../../Format.js";

export class writeNow extends Format
{
	name       = "WriteNow Document";
	website    = "http://fileformats.archiveteam.org/wiki/WriteNow";
	magic      = ["WriteNow document"];
	converters = ["soffice"];
}
