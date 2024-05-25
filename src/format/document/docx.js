import {Format} from "../../Format.js";

export class docx extends Format
{
	name           = "Office Open XML";
	website        = "http://fileformats.archiveteam.org/wiki/DOCX";
	ext            = [".docx", ".docm", ".dotx"];
	forbidExtMatch = true;
	magic          = ["Microsoft OOXML", "Word Microsoft Office Open XML Format document", "Microsoft Word 2007+ Zip archive", /^fmt\/(412|523|597)( |$)/];
	converters     = ["soffice[format:MS Word 2007 XML]", "soffice[format:MS Word 2007 XML Template]", "soffice[format:MS Word 2003 XML]"];
}
