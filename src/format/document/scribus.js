import {Format} from "../../Format.js";

export class scribus extends Format
{
	name           = "Scribus Document";
	website        = "http://fileformats.archiveteam.org/wiki/Scribus";
	ext            = [".sla", ".scd"];
	forbidExtMatch = true;
	magic          = ["Scribus document", "application/vnd.scribus", /^Scribus Document/, /^fmt\/1091( |$)/];
	converters     = dexState => [
		"scribus[outType:pdf]",

		// starting in scribus 1.7, scribus started being very picky about control characters or other invalid characters in the input file, so we pre-lint the XML file, strip the XML header and pass it to scribus
		`xmllint -> sed[op:1d][ext:${dexState.original.input.ext}] -> scribus[outType:pdf]`
	];
}
