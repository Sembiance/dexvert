import {Format} from "../../Format.js";

export class docx extends Format
{
	name           = "Office Open XML";
	website        = "http://fileformats.archiveteam.org/wiki/DOCX";
	ext            = [".docx", ".docm", ".dotx"];
	forbidExtMatch = true;
	magic          = ["Microsoft OOXML", "Word Microsoft Office Open XML Format document"];
	converters     = ["soffice"];
}
