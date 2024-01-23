import {Format} from "../../Format.js";

export class starOfficePresentation extends Format
{
	name           = "StarOffice Presentation";
	website        = "http://fileformats.archiveteam.org/wiki/StarOffice_binary_formats";
	ext            = [".sdd"];
	forbidExtMatch = true;
	magic          = ["StarOffice", /^x-fmt\/360( |$)/];
	weakMagic      = ["StarOffice"];
	converters     = ["soffice[format:StarOffice Presentation]"];
}
