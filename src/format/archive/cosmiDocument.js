import {Format} from "../../Format.js";

export class cosmiDocument extends Format
{
	name           = "COSMI Document";
	website        = "http://fileformats.archiveteam.org/wiki/COSMI_MultiMedia";
	ext            = [".pub", ".bro", ".bcd", ".crd", ".dtp"];
	forbidExtMatch = true;
	magic          = ["COSMI document"];
	converters     = ["foremost"];
}
