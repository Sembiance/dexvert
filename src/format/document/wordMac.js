import {Format} from "../../Format.js";

export class wordMac extends Format
{
	name       = "Macintosh Word Document";
	website    = "http://fileformats.archiveteam.org/wiki/Microsoft_Word_for_Macintosh";
	magic      = ["Word for the Macintosh document", "Microsoft Word for Macintosh", /^x-fmt\/(1|64|65)( |$)/];
	converters = ["soffice"];
}
