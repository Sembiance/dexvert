import {Format} from "../../Format.js";

export class openOfficeWriter extends Format
{
	name           = "Open Office Writer Document";
	website        = "http://fileformats.archiveteam.org/wiki/OpenOffice.org_XML";
	ext            = [".sxw", ".stw"];
	forbidExtMatch = true;
	magic          = ["OpenOffice.org 1.x Writer document", /^fmt\/(128|136)( |$)/];
	converters     = ["soffice[matchType:magic]"];
}
