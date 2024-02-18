import {Format} from "../../Format.js";

export class gedcom extends Format
{
	name           = "GEDCOM Genealogy Text";
	website        = "http://fileformats.archiveteam.org/wiki/GEDCOM";
	ext            = [".ged"];
	forbidExtMatch = true;
	magic          = ["GEDCOM genealogy text", "GEDCOM Family History", /^fmt\/851( |$)/];
	untouched      = true;
	metaProvider   = ["text"];
}
